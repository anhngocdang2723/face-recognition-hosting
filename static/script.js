function previewImage(input, previewId) {
    const file = input.files[0];
    const preview = document.getElementById(previewId);

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.innerHTML = '<img src="' + e.target.result + '" alt="Image Preview">';
        }
        reader.readAsDataURL(file);
    } else {
        preview.innerHTML = '';
    }
}

document.getElementById('file1').addEventListener('change', function() {
    previewImage(this, 'preview1');
});

document.getElementById('file2').addEventListener('change', function() {
    previewImage(this, 'preview2');
});

document.getElementById('uploadForm').onsubmit = async function(event) {
    event.preventDefault();
    document.getElementById('result').textContent = "Đang xử lý...";
    document.getElementById('result').classList.add('loading');

    let formData = new FormData(this);
    let response = await fetch('/upload-images', {
        method: 'POST',
        body: formData
    });

    let result = await response.json();
    document.getElementById('result').textContent = result.result;
    document.getElementById('result').classList.remove('loading');
}
