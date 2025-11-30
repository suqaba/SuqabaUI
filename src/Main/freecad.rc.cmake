/////////////////////////////////////////////////////////////////////////////
// For info about the file structrure see
// https://docs.microsoft.com/en-us/windows/win32/menurc/versioninfo-resource
// and
// https://docs.microsoft.com/en-us/windows/win32/menurc/stringfileinfo-block

// Icon
//
// Icon with lowest ID value placed first to ensure application icon
// remains consistent on all systems.
IDI_ICON1               ICON    DISCARDABLE     "icon.ico"

// File info for the FreeCAD.exe
//
1 VERSIONINFO
FILEVERSION ${PACKAGE_VERSION_MAJOR},${PACKAGE_VERSION_MINOR},${PACKAGE_VERSION_PATCH},${PACKAGE_BUILD_VERSION}
BEGIN
    BLOCK "StringFileInfo"
    BEGIN
        BLOCK "040904b0" // 409 stands for US English
        BEGIN
            VALUE "CompanyName", "$Suqaba Team"
            VALUE "FileDescription", "SuqabaUI main executable"
            VALUE "InternalName", "SuqabaUI.exe"
            VALUE "LegalCopyright", "Copyright (C) 2025"
            VALUE "OriginalFilename", "SuqabaUI.exe"
            VALUE "ProductName", "SuqabaUI"
            VALUE "ProductVersion", "${PACKAGE_VERSION}${PACKAGE_VERSION_SUFFIX}"
        END
    END
    BLOCK "VarFileInfo"
    BEGIN
        VALUE "Translation", 0x409, 1200 //US English, Unicode
    END
END
