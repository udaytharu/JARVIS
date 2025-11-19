Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this VBS file is located
currentPath = fso.GetParentFolderName(WScript.ScriptFullName)

' Build the full path to the batch file
batPath = currentPath & "\run_listen.bat"

' Check if the batch file exists
If Not fso.FileExists(batPath) Then
    ' Log error to a file
    Set logFile = fso.CreateTextFile(currentPath & "\vbs_error.log", True)
    logFile.WriteLine("[" & Now & "] Error: run_listen.bat not found at " & batPath)
    logFile.WriteLine("Current path: " & currentPath)
    logFile.WriteLine("Script full name: " & WScript.ScriptFullName)
    logFile.Close
    WScript.Quit 1
End If

' Convert to absolute path and wrap in quotes
batPath = Chr(34) & fso.GetAbsolutePathName(batPath) & Chr(34)

' Run the batch file hidden (0 = hidden window, False = do not wait)
shell.Run batPath, 0, False

