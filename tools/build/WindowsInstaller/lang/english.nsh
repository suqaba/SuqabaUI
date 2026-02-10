/*
FreeCAD Installer Language File
Language: English
*/

!insertmacro LANGFILE_EXT "English"

${LangFileString} TEXT_INSTALL_CURRENTUSER "(Installed for Current User)"

${LangFileString} TEXT_WELCOME "This wizard will guide you through the installation of $(^NameDA), $\r$\n\
				$\r$\n\
				$_CLICK"

#${LangFileString} TEXT_CONFIGURE_PYTHON "Compiling Python scripts..."

${LangFileString} TEXT_FINISH_DESKTOP "Create desktop shortcut"
${LangFileString} TEXT_FINISH_WEBSITE "Visit suqaba.com for the latest news"

#${LangFileString} FileTypeTitle "FreeCAD-Document"

#${LangFileString} SecAllUsersTitle "Install for all users?"
${LangFileString} SecFileAssocTitle "File associations"
${LangFileString} SecDesktopTitle "Desktop icon"

${LangFileString} SecCoreDescription "The SuqabaUI files."
#${LangFileString} SecAllUsersDescription "Install SuqabaUI for all users or just the current user."
${LangFileString} SecFileAssocDescription "Files with a .FCStd extension will automatically open in SuqabaUI."
${LangFileString} SecDesktopDescription "A SuqabaUI icon on the desktop."
#${LangFileString} SecDictionaries "Dictionaries"
#${LangFileString} SecDictionariesDescription "Spell-checker dictionaries that can be downloaded and installed."

#${LangFileString} PathName 'Path to the file $\"xxx.exe$\"'
#${LangFileString} InvalidFolder 'The file $\"xxx.exe$\" is not in the specified path.'

#${LangFileString} DictionariesFailed 'Download of dictionary for language $\"$R3$\" failed.'

#${LangFileString} ConfigInfo "The following configuration of SuqabaUI could take a while."

#${LangFileString} RunConfigureFailed "Could not run configure script."
${LangFileString} InstallRunning "The installer is already running!"
${LangFileString} AlreadyInstalled "SuqabaUI ${APP_SERIES_KEY2} is already installed!$\r$\n\
				Installing over existing installations is not recommended if the installed version$\r$\n\
				is a test release or if you have problems with your existing SuqabaUI installation.$\r$\n\
				In these cases better reinstall SuqabaUI.$\r$\n\
				Do you nevertheless want to install SuqabaUI over the existing version?"
${LangFileString} NewerInstalled "You are trying to install an older version of SuqabaUI than what you have installed.$\r$\n\
				  If you really want this, you must uninstall the existing SuqabaUI $OldVersionNumber before."

#${LangFileString} FinishPageMessage "Congratulations! SuqabaUI has been installed successfully.$\r$\n\
#					$\r$\n\
#					(The first start of SuqabaUI might take some seconds.)"
${LangFileString} FinishPageRun "Launch SuqabaUI"

${LangFileString} UnNotInRegistryLabel "Unable to find SuqabaUI in the registry.$\r$\n\
					Shortcuts on the desktop and in the Start Menu will not be removed."
${LangFileString} UnInstallRunning "You must close SuqabaUI first!"
${LangFileString} UnNotAdminLabel "You must have administrator privileges to uninstall SuqabaUI!"
${LangFileString} UnReallyRemoveLabel "Are you sure you want to completely remove SuqabaUI and all of its components?"
${LangFileString} UnFreeCADPreferencesTitle 'SuqabaUI$\'s user preferences'

#${LangFileString} SecUnProgDescription "Uninstalls xxx."
${LangFileString} SecUnPreferencesDescription 'Deletes SuqabaUI$\'s configuration$\r$\n\
						(folder $\"$AppPre\username\$\r$\n\
						$AppSuff\$\r$\n\
						${APP_DIR_USERDATA}$\")$\r$\n\
						for you or for all users (if you are admin).'
${LangFileString} DialogUnPreferences 'you chose to delete the SuqabaUIs user configuration.$\r$\n\
						This will also delete all installed SuqabaUI addons.$\r$\n\
						Do you agree with this?'
${LangFileString} SecUnProgramFilesDescription "Uninstall SuqabaUI and all of its components."
