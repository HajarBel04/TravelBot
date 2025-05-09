// pages/api/process-email.js
export default async function handler(req, res) {
    if (req.method !== 'POST') {
      return res.status(405).json({ message: 'Method not allowed' });
    }
  
    try {
      const { email } = req.body;
  
      if (!email) {
        return res.status(400).json({ message: 'Email content is required' });
      }
  
      // In a real application, this would call your backend API
      // For now, we'll simulate a call to your RAG system
      const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
      
      // Uncomment this in production to make actual API calls
      // const response = await fetch(`${backendUrl}/api/process-email`, {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //   },
      //   body: JSON.stringify({ email }),
      // });
      // 
      // if (!response.ok) {
      //   throw new Error(`Backend error: ${response.status}`);
      // }
      // 
      // const data = await response.json();
      // return res.status(200).json(data);
  
      // For demo purposes, simulate a response with mock data
      // This would be replaced with actual API calls in production
      const mockResponse = await simulateRagProcessing(email);
      
      // Add a deliberate delay to simulate processing time
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      return res.status(200).json(mockResponse);
    } catch (error) {
      console.error('Error processing email:', error);
      return res.status(500).json({ message: 'Error processing request', error: error.message });
    }
  }
  
  // This function simulates the response from the RAG system
  async function simulateRagProcessing(email) {
    // Extract destination from email (simple regex for demo)
    const destinationMatch = email.match(/(?:to|in|for)\s+([A-Za-z\s]+)(?:for|in|\.)/i);
    const destination = destinationMatch ? destinationMatch[1].trim() : 'Paris';
    
    // Extract duration
    const durationMatch = email.match(/(\d+)\s*(?:day|days|week|weeks)/i);
    const duration = durationMatch ? durationMatch[1] + ' days' : '7 days';
    
    // Extract travelers
    const travelersMatch = email.match(/(?:family of|with|for)\s+(\d+)/i);
    const travelers = travelersMatch ? travelersMatch[1] : '2';
    
    // Extract budget
    const budgetMatch = email.match(/budget.*?(\$?\d[\d,]*)/i);
    const budget = budgetMatch ? budgetMatch[1] : '$3000';
    
    // Extract interests
    let interests = 'sightseeing, local cuisine';
    if (email.toLowerCase().includes('beach')) interests = 'beaches, swimming, relaxation';
    if (email.toLowerCase().includes('mountain')) interests = 'hiking, nature, adventure';
    if (email.toLowerCase().includes('museum')) interests = 'museums, history, culture';
    
    // Generate a mock itinerary
    const proposal = generateMockItinerary(destination, parseInt(duration), interests);
    
    return {
      extracted_info: {
        destination,
        duration,
        travelers,
        budget,
        interests,
        travel_type: email.toLowerCase().includes('beach') ? 'beach vacation' : 
                    email.toLowerCase().includes('mountain') ? 'mountain adventure' : 
                    'cultural exploration'
      },
      packages: [
        {
          name: `${destination} Explorer`,
          location: destination,
          description: `Discover the best of ${destination} with this comprehensive package.`,
          activities: interests.split(', '),
          price: parseInt(budget.replace(/[$,]/g, ''))
        },
        {
          name: `${destination} Deluxe Experience`,
          location: destination,
          description: `Luxury travel package for an unforgettable ${destination} experience.`,
          activities: interests.split(', ').concat(['premium dining', 'exclusive tours']),
          price: parseInt(budget.replace(/[$,]/g, '')) * 1.5
        }
      ],
      proposal,
      timings: {
        extraction_ms: 450,
        generation_ms: 1200,
        total_ms: 1800
      }
    };
  }
  
  function generateMockItinerary(destination, days, interests) {
    const interestsList = interests.split(', ');
    
    let itinerary = `# ${days}-Day Itinerary for ${destination}\n\n`;
    
    // Add overview
    itinerary += `## Overview\n`;
    itinerary += `This personalized itinerary will help you explore the best of ${destination}. `;
    itinerary += `You'll experience ${interestsList.join(', ')}, and discover the local culture.\n\n`;
    
    // Add daily plans
    for (let i = 1; i <= days; i++) {
      itinerary += `## Day ${i}\n\n`;
      
      // Morning
      itinerary += `### Morning (8:00 AM - 12:00 PM)\n`;
      itinerary += `- Breakfast at Café ${['Soleil', 'Central', 'Riverside', 'Belvedere', 'Panorama'][i % 5]}\n`;
      itinerary += `- Visit the ${['famous', 'historic', 'renowned', 'popular', 'must-see'][i % 5]} ${destination} ${['Museum', 'Park', 'Cathedral', 'Market', 'Palace'][i % 5]}\n`;
      itinerary += `- Guided tour of the ${['Old Town', 'Historic District', 'Cultural Quarter', 'City Center', 'Waterfront'][i % 5]}\n\n`;
      
      // Afternoon
      itinerary += `### Afternoon (12:00 PM - 5:00 PM)\n`;
      itinerary += `- Lunch at ${['Restaurant Le Chef', 'Local Bistro', 'Traditional Eatery', 'Gourmet Kitchen', 'Seaside Dining'][i % 5]}\n`;
      itinerary += `- ${['Shopping at local boutiques', 'Relaxing at a café', 'Exploring hidden neighborhoods', 'Participating in a local workshop', 'Visiting an art gallery'][i % 5]}\n`;
      if (interestsList[i % interestsList.length]) {
        itinerary += `- ${capitalizeFirstLetter(interestsList[i % interestsList.length])} experience\n\n`;
      }
      
      // Evening
      itinerary += `### Evening (5:00 PM - 10:00 PM)\n`;
      itinerary += `- Dinner at ${['Michelin-starred', 'highly-rated', 'authentic', 'charming', 'popular'][i % 5]} restaurant ${['La Vue', 'The Garden', 'Seaside', 'Azure', 'Panorama'][i % 5]}\n`;
      itinerary += `- ${['Evening walk along the promenade', 'Cultural performance at the theater', 'Night tour of illuminated landmarks', 'Wine tasting experience', 'Local music performance'][i % 5]}\n\n`;
    }
    
    // Add practical information
    itinerary += `## Practical Information\n\n`;
    
    // Accommodations
    itinerary += `### Recommended Accommodations\n`;
    itinerary += `- Hotel ${destination} Plaza - 4-star centrally located hotel\n`;
    itinerary += `- ${destination} Boutique Suites - Charming mid-range option\n`;
    itinerary += `- The ${destination} Grand Resort - Luxury option with excellent amenities\n\n`;
    
    // Transportation
    itinerary += `### Transportation Options\n`;
    itinerary += `- Public transportation: Efficient metro and bus system\n`;
    itinerary += `- Taxi services: Readily available throughout the city\n`;
    itinerary += `- Rental car: Recommended for exploring the surrounding areas\n\n`;
    
    // Costs
    itinerary += `### Estimated Costs\n`;
    itinerary += `- Accommodations: $100-300 per night depending on luxury level\n`;
    itinerary += `- Meals: $30-80 per person per day\n`;
    itinerary += `- Attractions: $15-25 per attraction\n`;
    itinerary += `- Local transportation: $10-20 per day\n\n`;
    
    // Weather info
    itinerary += `## Weather Forecast\n`;
    itinerary += `- 2025-05-10: 22.5°C to 28.1°C, Precipitation: 0.0mm\n`;
    itinerary += `- 2025-05-11: 21.8°C to 27.5°C, Precipitation: 0.0mm\n`;
    itinerary += `- 2025-05-12: 22.0°C to 29.3°C, Precipitation: 0.0mm\n`;
    itinerary += `- 2025-05-13: 20.5°C to 26.8°C, Precipitation: 2.5mm\n`;
    itinerary += `- 2025-05-14: 21.3°C to 27.2°C, Precipitation: 0.5mm\n\n`;
    
    // Travel tips
    itinerary += `## Travel Tips\n\n`;
    itinerary += `### General Tips\n`;
    itinerary += `- Carry a photocopy of your passport and store the original in your hotel safe\n`;
    itinerary += `- Download offline maps before your trip\n`;
    itinerary += `- Learn a few basic phrases in the local language\n`;
    itinerary += `- Carry a reusable water bottle to stay hydrated\n\n`;
    
    itinerary += `### Local Customs\n`;
    itinerary += `- Greet locals with a smile and a nod\n`;
    itinerary += `- Tipping is ${['customary', 'optional but appreciated', 'not expected', 'typically included'][Math.floor(Math.random() * 4)]}\n`;
    itinerary += `- Dress modestly when visiting religious sites\n`;
    
    return itinerary;
  }
  
  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }