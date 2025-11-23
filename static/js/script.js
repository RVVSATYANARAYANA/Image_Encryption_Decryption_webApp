// Handle Encryption Form
document.getElementById('encryptForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    const fileInput = document.getElementById('encryptFile');
    const makeSquareCheckbox = document.getElementById('makeSquare');
    formData.append('file', fileInput.files[0]);
    formData.append('make_square', makeSquareCheckbox.checked);

    try {
        console.log('Submitting encryption form...');
        const response = await fetch('/encrypt', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        console.log('Encryption response:', result);
        
        const resultDiv = document.getElementById('encryptResult');
        if (result.error) {
            console.log('Error in encryption response:', result.error);
            resultDiv.innerHTML = `<div class="error">Error: ${result.error}</div>`;
        } else {
            console.log('Generating download links for encrypted image and key...');
            console.log('Encrypted image path:', result.encrypted_image);
            console.log('Key file path:', result.key_file);
            console.log('Encrypted download URL:', result.encrypted_download_url);
            console.log('Key download URL:', result.key_download_url);
            resultDiv.innerHTML = `
                <p>Encryption successful!</p>
                <p>Encrypted Image: <a href="${result.encrypted_download_url}" download="${result.encrypted_image.split('/').pop()}" class="download-btn">Download</a></p>
                <p>Key File: <a href="${result.key_download_url}" download="${result.key_file.split('/').pop()}" class="download-btn">Download</a></p>
                <img src="/${result.encrypted_image}?t=${new Date().getTime()}" alt="Encrypted Image">
            `;
        }
    } catch (error) {
        console.error('Encryption fetch error:', error);
        document.getElementById('encryptResult').innerHTML = `<div class="error">Error: ${error.message}</div>`;
    }
});

// Handle Decryption Form
document.getElementById('decryptForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    const fileInput = document.getElementById('decryptFile');
    const keyInput = document.getElementById('keyFile');
    formData.append('file', fileInput.files[0]);
    formData.append('key', keyInput.files[0]);

    try {
        console.log('Submitting decryption form...');
        const response = await fetch('/decrypt', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        console.log('Decryption response:', result);
        
        const resultDiv = document.getElementById('decryptResult');
        if (result.error) {
            console.log('Error in decryption response:', result.error);
            resultDiv.innerHTML = `<div class="error">Error: ${result.error}</div>`;
        } else {
            console.log('Generating download link for decrypted image...');
            console.log('Decrypted image path:', result.decrypted_image);
            console.log('Decrypted download URL:', result.decrypted_download_url);
            resultDiv.innerHTML = `
                <p>Decryption successful!</p>
                <p>Decrypted Image: <a href="${result.decrypted_download_url}" download="${result.decrypted_image.split('/').pop()}" class="download-btn">Download</a></p>
                <img src="/${result.decrypted_image}?t=${new Date().getTime()}" alt="Decrypted Image">
            `;
        }
    } catch (error) {
        console.error('Decryption fetch error:', error);
        document.getElementById('decryptResult').innerHTML = `<div class="error">Error: ${error.message}</div>`;
    }
});

// Adjust landing page elements dynamically for responsiveness
document.addEventListener('DOMContentLoaded', () => {
    // Function to adjust landing page elements based on screen size
    const adjustLandingPage = () => {
        const landingContainer = document.querySelector('.landing-container');
        if (landingContainer) {
            if (window.innerWidth <= 480) {
                landingContainer.style.padding = '1rem';
            } else if (window.innerWidth <= 768) {
                landingContainer.style.padding = '1.5rem';
            } else {
                landingContainer.style.padding = '2rem';
            }
        }
    };

    // Run on page load
    adjustLandingPage();

    // Run on window resize
    window.addEventListener('resize', adjustLandingPage);
});