import QtQuick
import QtQuick.Controls
import TrainsView

Column {
    id: root

    property Device device: model.object

    Text {
        text: root.device.name
    }

    Button {
        text: "Disconnect"
        onClicked: root.device.disconnect()
    }

    Button {
        text: "Forward"
        onClicked: root.device.send("fwd")
    }

    Button {
        text: "Reverse"
        onClicked: root.device.send("rev")
    }

    Button {
        text: "Stop"
        onClicked: root.device.send("stp")
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
