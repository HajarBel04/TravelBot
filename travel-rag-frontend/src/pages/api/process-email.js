// pages/api/process-email.js
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const { email } = req.body;
    
    if (!email) {
      return res.status(400).json({ message: 'Email text is required' });
    }
    
    // FIXED: Use the correct endpoint URL
    const response = await fetch('http://localhost:8000/api/process-email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      throw new Error(`Backend API responded with status: ${response.status}, message: ${errorText}`);
    }
    
    const data = await response.json();
    return res.status(200).json(data);
  } catch (error) {
    console.error('Error processing email:', error);
    return res.status(500).json({ 
      message: 'Error processing email', 
      error: error.message 
    });
  }
}