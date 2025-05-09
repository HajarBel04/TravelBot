// pages/api/stats.js
export default async function handler(req, res) {
    if (req.method !== 'GET') {
      return res.status(405).json({ message: 'Method not allowed' });
    }
  
    try {
      // In a real application, this would call your backend API to get stats
      // For now, we'll return mock stats
      const mockStats = {
        cache: {
          response_cache: {
            total_entries: 42,
            memory_usage_kb: 1240,
            hit_rate: 0.78
          },
          destination_cache: {
            total_entries: 18,
            destinations: ['Paris', 'Rome', 'Maldives', 'New York', 'Tokyo'],
            hit_rate: 0.85
          }
        },
        vector_store: {
          documents: 156,
          index_size_mb: 24.5,
          last_updated: '2025-05-08T14:23:45Z'
        },
        performance: {
          timestamp: '2025-05-09T08:15:32Z',
          extraction: {
            extraction_completeness: 0.75,
            fields_extracted: 5.2,
            process_time_ms: 432
          },
          retrieval: {
            location_diversity: 0.82,
            packages_count: 3.5,
            theme_diversity: 0.68,
            process_time_ms: 321
          },
          generation: {
            quality_score: 0.89,
            structure_score: 0.92,
            information_density: 0.76,
            process_time_ms: 1247
          },
          end_to_end: {
            total_processing_time: 2135,
            efficiency_ratio: 4.2,
            sentence_count: 87
          }
        },
        usage: {
          total_requests: 325,
          unique_users: 48,
          popular_destinations: [
            { name: 'Paris', count: 42 },
            { name: 'Rome', count: 38 },
            { name: 'New York', count: 31 },
            { name: 'Tokyo', count: 27 },
            { name: 'Maldives', count: 23 }
          ]
        }
      };
  
      // Add a deliberate delay to simulate processing time
      await new Promise(resolve => setTimeout(resolve, 500));
      
      return res.status(200).json(mockStats);
    } catch (error) {
      console.error('Error fetching stats:', error);
      return res.status(500).json({ message: 'Error fetching stats', error: error.message });
    }
  }