// server.js
const express = require('express');
const cors = require('cors');
const { VideoIntelligenceServiceClient } = require('@google-cloud/video-intelligence');
const ytdl = require('ytdl-core');
const { Storage } = require('@google-cloud/storage');
const speech = require('@google-cloud/speech');
const ffmpeg = require('fluent-ffmpeg');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

// Configure Google Cloud
const storage = new Storage({
    keyFilename: '/Users/test/Downloads/client_secret_213162181375-f3tb8igst5qe005q9sf73jusldcmvtsa.apps.googleusercontent.com'
});
const speechClient = new speech.SpeechClient({
    keyFilename: '/Users/test/Downloads/client_secret_213162181375-f3tb8igst5qe005q9sf73jusldcmvtsa.apps.googleusercontent.com'
});

const bucketName = 'Web client 1';
const bucket = storage.bucket(bucketName);

app.post('/transcribe', async (req, res) => {
    try {
        const { videoId } = req.body;
        const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;
        
        // Download audio from YouTube
        const audioFilePath = path.join(__dirname, `${videoId}.mp3`);
        await downloadYouTubeAudio(videoUrl, audioFilePath);
        
        // Upload to Google Cloud Storage
        const gcsFilePath = `audio/${videoId}.mp3`;
        await bucket.upload(audioFilePath, {
            destination: gcsFilePath
        });
        
        // Configure transcription request
        const audio = {
            uri: `gs://${bucketName}/${gcsFilePath}`
        };
        
        const config = {
            encoding: 'MP3',
            sampleRateHertz: 16000,
            languageCode: 'en-US',
            enableAutomaticPunctuation: true,
            model: 'video'
        };
        
        const request = {
            audio: audio,
            config: config
        };
        
        // Start transcription
        const [operation] = await speechClient.longRunningRecognize(request);
        const [response] = await operation.promise();
        
        // Process transcription result
        const transcription = response.results
            .map(result => result.alternatives[0].transcript)
            .join('\n');
        
        // Cleanup
        fs.unlinkSync(audioFilePath);
        await bucket.file(gcsFilePath).delete();
        
        res.json({ transcription });
    } catch (error) {
        console.error('Transcription error:', error);
        res.status(500).json({ error: error.message });
    }
});

async function downloadYouTubeAudio(url, outputPath) {
    return new Promise((resolve, reject) => {
        ytdl(url, { quality: 'highestaudio' })
            .pipe(ffmpeg()
                .toFormat('mp3')
                .on('error', reject)
                .on('end', resolve)
                .save(outputPath));
    });
}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});