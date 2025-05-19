import QtQuick
import QtQuick.Controls
import TrainsView

Rectangle {
    id: root

    property Device device: model.object

    color: "transparent"
    border.width: 1

    Column {
        anchors.fill: parent

        Text {
            text: root.device.name
        }

        Button {
            text: "Disconnect"
            onClicked: root.device.disconnect()
        }

        Text {
            text: "Speed " + speedSlider.value
        }

        Slider {
            id: speedSlider

            anchors.horizontalCenter: parent.horizontalCenter

            orientation: Qt.Vertical
            wheelEnabled: true
            from: -100
            to: 100
            stepSize: 10
            snapMode: Slider.SnapAlways

            Binding {
                target: root.device
                property: "speed"
                value: speedSlider.value
            }
        }

        Button {
            text: "Stop"
            onClicked: speedSlider.value = 0
        }

        Text {
            text: "Voltage " + (root.device.voltage / 1000).toFixed(1) + " V"
        }

        Rectangle {
            id: detectedColor
            width: 50
            height: 50
            border.width: 2
            color: root.device.color
        }
    }
}
