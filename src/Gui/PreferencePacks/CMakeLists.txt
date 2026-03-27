SET(PreferencePacks_Files
    "package.xml")

SET(PreferencePacks_Directories
    "FreeCAD Classic"
    "Dark behave"
    "FreeCAD Light"
    "FreeCAD Dark"
    OpenTheme)

ADD_CUSTOM_TARGET(PreferencePacks_data ALL
                  SOURCES ${PreferencePacks_Files} ${PreferencePacks_Directories})

FILE(COPY ${PreferencePacks_Files} ${PreferencePacks_Directories}
     DESTINATION "${CMAKE_BINARY_DIR}/${CMAKE_INSTALL_DATADIR}/Gui/PreferencePacks"
     PATTERN ".git" EXCLUDE
     PATTERN ".github" EXCLUDE)

INSTALL(FILES ${PreferencePacks_Files}
        DESTINATION ${CMAKE_INSTALL_DATADIR}/Gui/PreferencePacks)

INSTALL(DIRECTORY ${PreferencePacks_Directories}
        DESTINATION ${CMAKE_INSTALL_DATADIR}/Gui/PreferencePacks
        PATTERN ".git" EXCLUDE
        PATTERN ".github" EXCLUDE)
