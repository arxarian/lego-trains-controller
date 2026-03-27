import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window

    visible: true
    width: 800
    height: 800
    title: "Lego Trains Controller"
    color: "lightblue"

    Component.onCompleted: {
        Globals.editMode = Qt.binding(function() { return tabBar.currentIndex === 1 })
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Text {
            text: "Welcome to Lego Trains Controller!"
            font.pixelSize: 24
            horizontalAlignment: Text.AlignHCenter

            Layout.preferredHeight: contentHeight + 5
            Layout.fillWidth: true

            Rectangle {
                z: -1
                anchors.fill: parent
                color: "gold"
            }
        }

        TabBar {
            id: tabBar

            Layout.fillWidth: true

            TabButton { text: "Run Mode" }
            TabButton { text: "Edit Mode" }
            TabButton { text: "Debug Features" }
        }

        Item {
            clip: true

            Layout.fillHeight: true
            Layout.fillWidth: true

            TrackCanvas {
                anchors.fill: parent
            }

            RunPanel {
                anchors.fill: parent
                anchors.margins: 5
                visible: tabBar.currentIndex === 0
                z: 1
            }

            EditPanel {
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: 5
                visible: tabBar.currentIndex === 1
                z: 1
            }

            DebugPanel {
                anchors.top: parent.top
                anchors.right: parent.right
                anchors.margins: 5
                visible: tabBar.currentIndex === 2
                z: 1
            }
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
