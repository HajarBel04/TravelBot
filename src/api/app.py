# Add these new imports at the top
from enhanced_proposal_generator import ProposalGenerator
from optimized_vector_store import OptimizedVectorStore 
from response_caching_system import ResponseCache, DestinationCache
from rag_evaluation_metrics import RAGEvaluator
import time

# Add these before the app definition
response_cache = ResponseCache(cache_dir=str(project_root / "cache" / "responses"))
destination_cache = DestinationCache(cache_dir=str(project_root / "cache" / "destinations"))
evaluator = RAGEvaluator(metrics_dir=str(project_root / "metrics"))

# Replace the startup_event function with this enhanced version
@app.on_event("startup")
async def startup_event():
    global _vector_store, _retriever, _proposal_generator
    
    try:
        # Check if Ollama is running
        ollama = OllamaWrapper()
        ollama.generate("Test", "Test connection")
        logger.info("Successfully connected to Ollama")
        
        # Load travel packages
        packages_path = project_root / "data" / "synthetic" / "travel_packages.json"
        with open(packages_path, 'r') as f:
            data = json.load(f)
            packages = data.get('packages', [])
        
        logger.info(f"Loaded {len(packages)} travel packages")
        
        # Initialize enhanced vector store
        vector_store = OptimizedVectorStore(
            store_path=str(project_root / "data" / "embeddings" / "optimized_vector_store.pkl")
        )
        
        # Check if vector store has documents
        if not vector_store.get_documents():
            logger.info("Creating new vector store...")
            # Add to vector store
            vector_store.add_documents(packages)
            logger.info(f"Added {len(packages)} packages to vector store")
        else:
            logger.info("Loaded existing vector store")
        
        # Create retriever and proposal generator
        retriever = Retriever(vector_store)
        proposal_generator = ProposalGenerator()
        
        # Store components in app state
        app.state.vector_store = vector_store
        app.state.retriever = retriever
        app.state.proposal_generator = proposal_generator
        app.state.response_cache = response_cache
        app.state.destination_cache = destination_cache
        app.state.evaluator = evaluator
        
        # Also store in global variables as fallback
        _vector_store = vector_store
        _retriever = retriever
        _proposal_generator = proposal_generator
        
        logger.info("Travel RAG API initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Travel RAG API: {e}")
        logger.error("Will attempt to initialize components on-demand when endpoints are called")

# Replace the process_email endpoint with this enhanced version
@app.post("/process-email")
async def process_email(request: Request):
    try:
        # Parse request body
        data = await request.json()
        email_text = data.get("email", "")
        
        if not email_text:
            raise HTTPException(status_code=400, detail="Email text is required")
            
        # Try cache first
        cached_result = response_cache.get(email_text)
        if cached_result:
            logger.info("Using cached response")
            return cached_result
        
        start_time = time.time()
        
        # Process the email
        extractor = EmailExtractor()
        extracted_info = extractor.extract_from_email(email_text)
        
        # Evaluate extraction
        extraction_eval = evaluator.evaluate_extraction(email_text, extracted_info)
        
        # Retrieve relevant packages - try app state first, then globals
        try:
            if hasattr(app.state, 'retriever') and app.state.retriever is not None:
                retriever = app.state.retriever
                logger.info("Using retriever from app state")
            elif _retriever is not None:
                retriever = _retriever
                logger.info("Using retriever from global variable")
            else:
                # Create a new retriever as a last resort
                logger.info("Creating new retriever instance")
                vector_store = OptimizedVectorStore()
                if not vector_store.get_documents():
                    # Load packages
                    packages_path = project_root / "data" / "synthetic" / "travel_packages.json"
                    with open(packages_path, 'r') as f:
                        data = json.load(f)
                        packages = data.get('packages', [])
                    
                    # Add packages to vector store
                    vector_store.add_documents(packages)
                
                retriever = Retriever(vector_store)
                
            # Build query and retrieve packages
            query = retriever.build_query(extracted_info)
            packages = retriever.retrieve_relevant_packages(query, top_k=3)
            
            # Evaluate retrieval
            retrieval_eval = evaluator.evaluate_retrieval(query, packages)
            
            # Get or create proposal generator
            if hasattr(app.state, 'proposal_generator') and app.state.proposal_generator is not None:
                proposal_generator = app.state.proposal_generator
            elif _proposal_generator is not None:
                proposal_generator = _proposal_generator
            else:
                proposal_generator = ProposalGenerator()
            
            # Generate proposal
            generation_start = time.time()
            proposal = proposal_generator.generate_proposal(extracted_info, packages)
            generation_time = time.time() - generation_start
            
            # Evaluate generation
            generation_eval = evaluator.evaluate_generation(extracted_info, packages, proposal)
            
            # Evaluate end-to-end
            total_time = time.time() - start_time
            end_to_end_eval = evaluator.evaluate_end_to_end(email_text, proposal, total_time)
            
            # Format package info for response
            formatted_packages = []
            for package in packages:
                formatted_packages.append({
                    "name": package.get("name", ""),
                    "location": package.get("location", ""),
                    "duration": package.get("duration", ""),
                    "price": package.get("price", 0),
                    "activities": package.get("activities", []),
                    "description": package.get("description", "")
                })
            
            # Prepare result
            result = {
                "extracted_info": extracted_info,
                "query": query,
                "packages": formatted_packages,
                "proposal": proposal,
                "timings": {
                    "extraction_ms": (generation_start - start_time) * 1000,
                    "generation_ms": generation_time * 1000,
                    "total_ms": total_time * 1000
                },
                "metrics": {
                    "extraction_score": extraction_eval["metrics"].get("extraction_completeness", 0),
                    "generation_score": generation_eval["metrics"].get("quality_score", 0)
                }
            }
            
            # Cache the result
            response_cache.put(email_text, result)
            
            # Cache destination data
            if extracted_info.get('destination'):
                destination = extracted_info.get('destination')
                destination_cache.cache_destination_data(destination, {
                    'name': destination,
                    'packages': packages,
                    'query': query
                })
            
            return result
        except Exception as e:
            logger.error(f"Error in retrieval or proposal generation: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add this new endpoint for stats
@app.get("/stats")
async def get_stats():
    try:
        # Get statistics about the system
        stats = {
            "cache": {
                "response_cache": {
                    "total_entries": len(response_cache.cache),
                    "memory_usage_kb": sys.getsizeof(response_cache.cache) / 1024
                },
                "destination_cache": {
                    "total_entries": len(destination_cache.destinations),
                    "destinations": destination_cache.get_all_destinations()
                }
            },
            "vector_store": {
                "documents": len(_vector_store.get_documents()) if _vector_store else 0
            },
            "performance": evaluator.get_summary_report() if hasattr(evaluator, "get_summary_report") else {}
        }
        
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return {"status": "error", "message": str(e)}