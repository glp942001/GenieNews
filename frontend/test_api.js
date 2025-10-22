// Quick test to verify the API call works
const API_BASE_URL = 'http://localhost:8000/api';

async function testAudioAPI() {
  try {
    console.log('Testing API call to:', `${API_BASE_URL}/audio/daily-segment/`);
    
    const response = await fetch(`${API_BASE_URL}/audio/daily-segment/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    console.log('Response status:', response.status);
    console.log('Response headers:', response.headers);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Response data:', data);
    
    return {
      success: data.success,
      audioUrl: data.segment?.audio_url,
      scriptText: data.segment?.script_text,
      date: data.segment?.date,
      articleCount: data.segment?.article_count,
      error: null
    };
  } catch (error) {
    console.error('Error in testAudioAPI:', error);
    return {
      success: false,
      audioUrl: null,
      scriptText: null,
      date: null,
      articleCount: 0,
      error: error.message
    };
  }
}

// Run the test
testAudioAPI().then(result => {
  console.log('Final result:', result);
});
