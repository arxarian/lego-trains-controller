import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Popup {
    id: root

    parent: Overlay.overlay
    dim: true

    background: Rectangle {
        radius: 10
    }

    ColumnLayout {
        anchors.fill: parent

        Item {
            Layout.fillHeight: true
            Layout.fillWidth: true

            ListView {
                id: view
                anchors.fill: parent
                anchors.margins: 15
                model: devices.discovered
                delegate: Rectangle {
                    height: 30
                    width: view.width

                    color: view.currentIndex === index ? "lightblue" : "white"

                    MouseArea {
                        anchors.fill: parent
                        onClicked: view.currentIndex = index
                    }

                    Text {
                        anchors.fill: parent
                        text: modelData
                    }
                }
            }

            BusyIndicator {
                visible: view.count < 1
                anchors.fill: parent
                anchors.margins: 50
            }
        }

        RowLayout {
            Layout.fillHeight: true
            Layout.fillWidth: true

            Button {
                text: "Close"
                onClicked: root.close()
            }

            Item {
                Layout.fillWidth: true
            }

            Button {
                enabled: view.currentIndex > -1
                text: "Connect"
                onClicked: {
                    devices.connect_to(devices.discovered[view.currentIndex])
                    root.close()
                }
            }
        }
    }
}
