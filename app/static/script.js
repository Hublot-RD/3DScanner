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
    // Detail
    var detailSlider = document.getElementById('objectDetailSlider');
    var detailText = document.getElementById('objectDetailText');
    // Name
    var nameField = document.getElementById('objectNameField');
    var nameText = document.getElementById('objectNameText');
    // USB Device
    var usbDeviceDropdown = document.getElementById('usbDeviceDropdown');
    // More options
    var showMoreOptionButton = document.getElementById('showMoreOptionButton');
    var hideMoreOptionButton = document.getElementById('hideMoreOptionButton');
    var moreOptionContainer = document.getElementById('moreOptionContainer');
    // Flash
    var lightToggleButton = document.getElementById('lightToggleButton');
    // Go
    var goButton = document.getElementById('goButton');
    // Stop
    var stopButton = document.getElementById('stopButton');
    // Progress
    var progressContainer = document.getElementById('progressContainer');
    // var progressText = document.getElementById('progressText');
    // var progressBar = document.getElementById('progressBar');
    // var progressBarIndicator = document.getElementById('progressBarIndicator');

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
            heightText.innerHTML = String(value) + 'cm';
        } else {
            heightText.innerHTML = 'Une erreur est survenue';
        }
    }

    function updateDetailText(value) {
        switch(parseInt(value)) {
            case 0:
                detailText.innerHTML = 'faible';
              break;
            case 1:
                detailText.innerHTML = 'moyen';
              break;
            case 2:
                detailText.innerHTML = 'fort';
              break;
            default:
                detailText.innerHTML = 'Une erreur est survenue.'; // mettre la valeur en string ici
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
        var bounded_value = Math.max(0, Math.min(100, value));
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
    
    // Event listners
    heightSlider.oninput = function() {
        updateHeightText(this.value);
    }

    detailSlider.oninput = function() {
        updateDetailText(this.value);
    }

    nameField.oninput = function() {
        nameText.innerHTML = formatNameText(this.value) + '000.jpg';
    }

    refreshImageCameraButton.addEventListener('click', function() {
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

    lightToggleButton.addEventListener('change', function() {
        socket.emit('light_toggled', lightToggleButton.checked)
    });

    goButton.addEventListener('click', function() {
        // Send infos to python code
        var heightSliderValue = heightSlider.value;
        var detailSliderValue = detailSlider.value;
        var nameFieldValue = formatNameText(nameField.value);
        var usb_device = usbDeviceDropdown.options[usbDeviceDropdown.selectedIndex].value
        var infos =  {height: heightSliderValue, 
                      detail: detailSliderValue, 
                      obj_name: nameFieldValue,
                      usb_storage_loc: usb_device,
                    }
        
        socket.emit('start_capture',  infos);

        // show new elements to web page
        goButton.disabled = true;
        stopButton.style.display = 'inline';
        progressContainer.style.display = 'inline';
    });

    stopButton.addEventListener('click', function() {
        socket.emit('stop_capture');
        
        // hide elements from page
        goButton.disabled = false;
        stopButton.style.display = 'none';
        progressContainer.style.display = 'none';
        
        // reset necessary elements
        updateProgressBar(0);
        updateProgressText();
    });

    usbDeviceDropdown.addEventListener('click', function() {
        console.log('click detected')
        socket.emit('refresh_usb_list')
    });
    
    socket.on('update_usb_list', function(data) {
        updateusbDeviceDropdown(data.device_list); 
    });

    socket.on('update_progress', function(data) {
        updateProgressBar(data.progress_value);
        updateProgressText(data.text_value);
    });

    socket.on('update_image', function(data) {
        updateImageCamera(data.filename);
    });
});