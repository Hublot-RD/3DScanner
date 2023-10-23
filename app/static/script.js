document.addEventListener('DOMContentLoaded', function() {
    // Socket to connect to backend
    var socket = io.connect('http://' + location.hostname + ':' + location.port);
    socket.on('connect', function() {
        console.log('Connected to server');
    })
    // Image
    var imageCamera = document.getElementById('imageCamera');
    var refreshImageCameraButton = document.getElementById('refreshImageCameraButton'); 
    // Height
    var heightSlider = document.getElementById('objectHeightSlider');
    var heightText = document.getElementById('objectHeightText');
    // Name
    var nameField = document.getElementById('objectNameField');
    var nameText = document.getElementById('objectNameText');
    // USB Device
    var usbDeviceDropdown = document.getElementById('usbDeviceDropdown');
    // More options
    var showMoreOptionButton = document.getElementById('showMoreOptionButton');
    var hideMoreOptionButton = document.getElementById('hideMoreOptionButton');
    var moreOptionContainer = document.getElementById('moreOptionContainer');
    var speedRotationDropdown = document.getElementById('speedRotationDropdown');
    var stepRotationDropdown = document.getElementById('stepRotationDropdown');
    var speedTranslationDropdown = document.getElementById('speedTranslationDropdown');
    var stepTranslationDropdown = document.getElementById('stepTranslationDropdown');
    // var exposureSlider = document.getElementById('exposureSlider')
    var flashCheckbox = document.getElementById('flashCheckbox');
    // Go, Stop, OK
    var goButton = document.getElementById('goButton');
    var stopButton = document.getElementById('stopButton');
    var okButton = document.getElementById('okButton');
    // Status
    var statusCircle = document.getElementById('statusCircle');
    var stateScanner = 'ready';
    // Progress
    var progressContainer = document.getElementById('progressContainer');
    var progressText = document.getElementById('progressText');
    var progressBar = document.getElementById('progressBar');
    var progressBarIndicator = document.getElementById('progressBarIndicator');
    var forecastedTime = document.getElementById('forecastedTime');

    // Blink functions for LEDs
    function statusCircleBlinkError() {
        if (stateScanner == 'error') {
            var currentColor = statusCircle.style.backgroundColor;
            statusCircle.style.backgroundColor = (currentColor === 'red') ? 'darkred' : 'red';
        }
    }

    function statusCircleBlinkCapture() {
        if (stateScanner == 'capture') {
            var currentColor = statusCircle.style.backgroundColor;
            statusCircle.style.backgroundColor = (currentColor === 'greenyellow') ? 'green' : 'greenyellow';
        }
    }

    function statusCircleEnd() {
        if (stateScanner == 'end') {
            statusCircle.style.backgroundColor = 'greenyellow';
        }
    }

    function statusCircleReady() {
        if (stateScanner == 'ready') {
            statusCircle.style.backgroundColor = 'green';
        }
    }

    setInterval(statusCircleBlinkError, 200);
    setInterval(statusCircleBlinkCapture, 100);
    setInterval(statusCircleEnd, 1000);
    setInterval(statusCircleReady, 1000);

    // Update functions
    function updateImageCamera(filename) {
        if (filename) {
            console.log("filename is not empty!");
            console.log('/cam_imgs/' + filename);
            // imageCamera.src ="{{ url_for('serve_image', filename='" + String(filename) + "') }}"
            imageCamera.src = '/cam_imgs/' + filename;
            // imageCamera.src = 'static/cam_imgs/preview.jpg'
        } else {
            console.error("Error: Filename is empty!");
        }
    }

    function updateHeightText(value) {
        if (value) {
            heightText.innerHTML = String(value) + 'mm';
        } else {
            heightText.innerHTML = 'Une erreur est survenue';
        }
    }

    function updateusbDeviceDropdown(usbDeviceList) {      
        // Remove existing options
        while (usbDeviceDropdown.firstChild) {
            usbDeviceDropdown.removeChild(usbDeviceDropdown.firstChild);
        }

        // Add new options
        usbDeviceList.push('Aucun')
        usbDeviceList.forEach(function(option) {
            var optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            usbDeviceDropdown.appendChild(optionElement);
        });
    }

    function formatNameText(value) {
        text = value.trim();
        if (value) {
            return text;
        } else {
            return 'capture';
        }
    }

    function updateProgressBar(value) {
        var bounded_value = Math.max(0, Math.min(100, value)).toFixed(2);
        progressBar.value = bounded_value;
        progressBarIndicator.innerHTML = String(bounded_value) + '%';
    }

    function updateProgressText(value) {
        if (value) {
            progressText.innerHTML = String(value);
        } else {
            progressText.innerHTML = 'Démarrage de la capture ...';
        }
    }

    function updateProgressTime(value) {
        forecastedTime.innerHTML = String(value);
    }
    
    // Event listners
    heightSlider.oninput = function() {
        updateHeightText(this.value);
    }

    nameField.oninput = function() {
        nameText.innerHTML = formatNameText(this.value) + '000.jpg';
    }

    refreshImageCameraButton.addEventListener('click', function() {
        refreshImageCameraButton.disabled = true;
        socket.emit('refresh_preview');
    });

    showMoreOptionButton.addEventListener('click', function() {
        hideMoreOptionButton.style.display = 'inline';
        moreOptionContainer.style.display = 'inline';
        showMoreOptionButton.style.display = 'none';
    });

    hideMoreOptionButton.addEventListener('click', function() {
        showMoreOptionButton.style.display = 'inline';
        moreOptionContainer.style.display = 'none';
        hideMoreOptionButton.style.display = 'none';
    });

    goButton.addEventListener('click', function() {
        // Send infos to python code
        var heightValue = heightSlider.value;
        var namedValue = formatNameText(nameField.value);
        var speedRotationValue = speedRotationDropdown.options[speedRotationDropdown.selectedIndex].value;
        var stepRotationValue = stepRotationDropdown.options[stepRotationDropdown.selectedIndex].value;
        var speedTranslationValue = speedTranslationDropdown.options[speedTranslationDropdown.selectedIndex].value;
        var stepTranslationValue = stepTranslationDropdown.options[stepTranslationDropdown.selectedIndex].value;
        var usbDeviceValue = usbDeviceDropdown.options[usbDeviceDropdown.selectedIndex].value;
        var flashCheckboxValue = flashCheckbox.checked;
        var infos =  {OBJ_HEIGHT: heightValue, 
                      OBJ_NAME: namedValue,
                      USB_STORAGE_LOC: usbDeviceValue,
                      MOTOR_TURNTABLE_SPEED: speedRotationValue,
                      MOTOR_TURNTABLE_STEP: stepRotationValue,
                      MOTOR_CAMERA_SPEED: speedTranslationValue,
                      MOTOR_CAMERA_STEP: stepTranslationValue,
                      FLASH_ENABLED: flashCheckboxValue,
                    };
        
        socket.emit('start_capture',  infos);

        // show new elements to web page
        goButton.disabled = true;
        refreshImageCameraButton.disabled = true
        stopButton.style.display = 'inline';
        progressContainer.style.display = 'inline';
    });

    stopButton.addEventListener('click', function() {
        socket.emit('stop_capture');
        
        // hide elements from page
        goButton.disabled = false;
        refreshImageCameraButton.disabled = false
        stopButton.style.display = 'none';
        progressContainer.style.display = 'none';
        
        // reset necessary elements
        updateProgressBar(0);
        updateProgressText();
    });

    okButton.addEventListener('click', function() {
        socket.emit('ok_capture');
        okButton.style.display = 'none';
        goButton.disabled = false;
        refreshImageCameraButton.disabled = false
        progressContainer.style.display = 'none';
    });

    usbDeviceDropdown.addEventListener('click', function() {
        socket.emit('refresh_usb_list')
    });
    
    socket.on('update_usb_list', function(data) {
        updateusbDeviceDropdown(data.device_list); 
    });

    socket.on('update_progress', function(data) {
        updateProgressBar(data.progress_value);
        updateProgressText(data.text_value);
        updateProgressTime(data.time_value);
        stateScanner = String(data.state);
        if (data.state == 'end') {
            // Hide progress bar, indicator, stop button
            progressBar.style.display = 'none';
            progressBarIndicator.style.display = 'none';
            stopButton.style.display = 'none';
            // Show OK button
            okButton.style.display = 'inline';
        }
    });

    socket.on('update_image', function(data) {
        updateImageCamera(data.filename);
        refreshImageCameraButton.disabled = false;
    });
});