# JARVIS Backgroundloop


# How to enable auto-start:
* Right-click backgroundloop/install_startup.bat → Run as administrator.
  On next restart/sign-in, run_hidden.vbs will start automatically and launch the background listener.
# To disable:
* Run backgroundloop/uninstall_startup.bat (Admin).


This directory contains the background listening functionality for JARVIS AI 2.0, which continuously listens for the wake phrase "jarvis" and launches the main JARVIS application when detected.

## Files Overview

- **`listen.py`** - Main Python script that listens for voice commands
- **`run_listen.bat`** - Windows batch file to run the listener in background
- **`run_hidden.vbs`** - VBScript to run the batch file without visible console
- **`install_dependencies.bat`** - Automatic dependency installer
- **`test_connectivity.py`** - Network connectivity diagnostic tool
- **`../Requirements.txt`** - Python package requirements (in root directory)
- **`jarvis.log`** - Main application log
- **`listen.log`** - Detailed listener log
- **`error.log`** - Error-specific log

## Quick Start

1. **Install Dependencies**: Run `install_dependencies.bat` as administrator
2. **Test Connectivity**: Run `python test_connectivity.py` to check network
3. **Start Listener**: Run `run_listen.bat` or `run_hidden.vbs`

## Troubleshooting

### Common Issues

#### 1. "Batch file not found" Error
- **Problem**: Script can't find JARVIS_START.bat
- **Solution**: Ensure JARVIS_START.bat exists in the parent directory
- **Check**: Verify file path: `..\JARVIS_START.bat`

#### 2. Speech Recognition Connection Failures
- **Problem**: `[WinError 10060]` or `[Errno 11001] getaddrinfo failed`
- **Causes**: 
  - Internet connectivity issues
  - Firewall blocking connections
  - Antivirus software interference
- **Solutions**:
  - Run `test_connectivity.py` to diagnose
  - Check Windows Firewall settings
  - Temporarily disable antivirus
  - Restart router/modem

#### 3. Microphone Not Working
- **Problem**: "No microphone found or microphone is unavailable"
- **Solutions**:
  - Check microphone permissions in Windows
  - Ensure microphone is set as default device
  - Test microphone in Windows Sound settings
  - Restart audio services

#### 4. Python Import Errors
- **Problem**: Missing SpeechRecognition or PyAudio
- **Solution**: Run `install_dependencies.bat` as administrator
- **Alternative**: `pip install SpeechRecognition PyAudio`
- **Note**: pocketsphinx is optional for offline recognition

### Network Issues

#### Firewall Configuration
1. Open Windows Defender Firewall
2. Allow Python through firewall
3. Add exceptions for speech recognition services
4. Check if corporate firewall is blocking connections

#### Proxy/Corporate Network
- Configure proxy settings in Python if needed
- Contact IT department for speech recognition access
- Use offline recognition as fallback

### Performance Issues

#### High CPU Usage
- Adjust `energy_threshold` in `listen.py`
- Increase `timeout` values
- Use offline recognition when possible

#### False Triggers
- Adjust `energy_threshold` (higher = less sensitive)
- Modify `pause_threshold` for better phrase detection
- Train ambient noise calibration in quiet environment

## Configuration

### Customizing Wake Phrase
```bash
python listen.py --phrase "hey computer"
```

### Custom Batch File
```bash
python listen.py --bat "path/to/custom.bat"
```

### Environment Variables
- `PYTHONPATH` - Add project root for imports
- `SPEECH_RECOGNITION_TIMEOUT` - Custom timeout values

## Logging

### Log Files
- **`jarvis.log`**: High-level application events
- **`listen.log`**: Detailed speech recognition logs
- **`error.log`**: Error-specific information

### Log Levels
- INFO: Normal operation
- WARNING: Non-critical issues
- ERROR: Critical failures
- DEBUG: Detailed debugging (when enabled)

## Offline Recognition

The system includes fallback offline recognition using pocketsphinx:
- Automatically switches when online services fail
- Requires `pocketsphinx` package installation
- Less accurate but works without internet

## Dependencies

### Required Packages
- `SpeechRecognition` >= 3.8.1
- `PyAudio` >= 0.2.11

### Optional Packages
- `pocketsphinx` >= 0.1.15 (for offline recognition fallback)

### System Requirements
- Windows 10/11
- Python 3.7+
- Microphone access
- Internet connection (for online recognition)

## Support

If issues persist:
1. Check all log files for detailed error information
2. Run connectivity tests
3. Verify system requirements
4. Check Windows Event Viewer for system errors
5. Ensure all dependencies are properly installed

## Security Notes

- The listener runs with user privileges
- No sensitive data is transmitted
- Microphone access is required
- Consider running in isolated environment if needed
