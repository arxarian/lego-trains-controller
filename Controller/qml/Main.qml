import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    visible: true
    width: 800
    height: 800
    title: "Lego Trains Controller"
    color: "lightblue"

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Text {
            Layout.preferredHeight: contentHeight + 5
            Layout.fillWidth: true

            text: "Welcome to Lego Trains Contoller!"
            font.pixelSize: 24
            horizontalAlignment: Text.AlignHCenter

            Rectangle {
                z: -1
                anchors.fill: parent
                color: "gold"
            }
        }

        Rectangle {
            color: Qt.darker("gold")

            Layout.preferredHeight: 25
            Layout.fillWidth: true

            Row {
                anchors.fill: parent

                Button {
                    id: runButton
                    text: "Run Mode"
                    autoExclusive: true
                    checkable: true
                    checked: true
                }

                Button {
                    text: "Edit Mode"
                    autoExclusive: true
                    checkable: true
                }
            }

        }

        StackLayout {
            currentIndex: runButton.checked ? 0 : 1
            Layout.fillHeight: true
            Layout.fillWidth: true

            RunScreen {}

            TrackEditorScreen {}
        }
    }

    DiscoverDevices {
        id: discoveredDevicesPopup
        anchors.centerIn: Overlay.overlay
        height: Overlay.overlay.height - 40
        width: Overlay.overlay.width - 40

        Connections {
            target: devices
            function onOpenDiscoverPopup() {
                discoveredDevicesPopup.open()
            }
        }
    }
}
