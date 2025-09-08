import QtQuick
import TrainView

Item
{
    id: root

    property int railId: -1
    property var model  // TODO - why var and not Connectors?

    Repeater {
        model: root.model
        delegate: Rectangle {
            id: item
            property Connector connector: model.object
            property real size: 100

            rotation: item.connector.angle * -22.5
            visible: item.connector.visible
            x: item.connector.rotator.x - item.size / 2
            y: item.connector.rotator.y - item.size / 2
            radius: item.size
            width: item.size
            height: item.size

            color: "#88FF00FF"

            SequentialAnimation on color {
                loops: Animation.Infinite
                ColorAnimation { from: "#88FF00FF"; to: "#55FF00FF"; duration: 1000; easing.type: Easing.InQuad }
                ColorAnimation { from: "#55FF00FF"; to: "#88FF00FF"; duration: 1000; easing.type: Easing.OutQuad }
            }

            MouseArea {
                anchors.fill: parent
                propagateComposedEvents: true
                onClicked: function(mouse) {
                    mouse.accepted = false
                    connectorRegister.addEvent(Globals.selectedType, root.railId, index)
                }
            }
        }
    }
}
