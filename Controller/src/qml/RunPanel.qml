import QtQuick
import QtQuick.Controls

Item {
    Row {
        anchors.top: parent.top
        anchors.right: parent.right
        spacing: 2

        Button {
            text: "Discover"
            onClicked: devices.discover()
        }

        Button {
            text: "Connect to Pybricks Hub"
            onClicked: devices.connect_to("Pybricks Hub")
        }

        Button {
            text: "Connect to Express Train"
            onClicked: devices.connect_to("Express Train")
        }

        Button {
            text: simulator.is_running ? "\u23F9 Stop Simulation" : "\u25B6 Simulate"
            enabled: network.has_graph
            onClicked: simulator.is_running ? simulator.stop() : simulator.start()
        }
    }

    ListView {
        id: trainView

        anchors.top: parent.top
        anchors.left: parent.left
        height: trains.count > 0 ? Math.min(300, parent.height) : 0
        width: trains.count > 0 ? Math.min(trains.count * 160, parent.width * 0.5) : 0

        model: trains
        orientation: Qt.Horizontal
        spacing: 5

        delegate: TrainControlPanel {
            height: trainView.height
            width: 150
        }
    }
}
