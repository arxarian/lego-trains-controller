import QtQuick
import TrainView

Item {
    id: root

    property var model

    Repeater {
        model: root.model
        delegate: Rectangle {
            property Connector connector: model.object

            x: connector.point.x - width / 2
            y: connector.point.y - height / 2
            z: 1

            visible: Globals.rotationPointsVisible
            width: 20
            height: 20
            radius: width
            opacity: 0.8
            color: "red"

            Rectangle {
                anchors.centerIn: parent
                width: 2
                height: 2
                color: "black"
            }
        }
    }
}
