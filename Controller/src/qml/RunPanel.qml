import QtQuick
import QtQuick.Controls

Item {
    Row {
        anchors.top: parent.top
        anchors.right: parent.right
        spacing: 2
        z: 1

        Button {
            text: simulator && simulator.is_running ? "\u23F9 Stop Simulation" : "\u25B6 Simulate"
            enabled: network && network.has_graph
            onClicked: {
                if (!simulator)
                    return
                simulator.is_running ? simulator.stop() : simulator.start()
            }
        }
    }

    ListView {
        id: trainView

        anchors.top: parent.top
        anchors.left: parent.left
        height: trains && trains.count > 0 ? Math.min(420, parent.height) : 0
        width: trains && trains.count > 0 ? Math.min(trains.count * 250, parent.width * 0.55) : 0

        model: trains
        orientation: Qt.Horizontal
        spacing: 5
        currentIndex: Globals.planningTrainIndex
        clip: true

        delegate: TrainControlPanel {
            height: trainView.height
            width: 240
            trainIndex: index
        }

        Connections {
            target: trains
            function onCountChanged() {
                if (!trains || trains.count === 0) {
                    Globals.planningTrainIndex = 0
                    return
                }
                if (Globals.planningTrainIndex >= trains.count)
                    Globals.planningTrainIndex = trains.count - 1
            }
        }
    }
}
