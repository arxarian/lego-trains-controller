import QtQuick
import TrainView

Item
{
    id: root

    property var model

    visible: Globals.markerPointsVisible && markerTypes.markersActive

    Repeater {
        model: root.model
        delegate: Rectangle {
            id: item
            property Marker marker: model.object
            property real size: 50

            visible: item.marker.visible
            x: item.marker.rotator.x - item.size / 2
            y: item.marker.rotator.y - item.size / 2
            rotation: item.marker.rotator.angle

            radius: item.size
            width: item.size
            height: item.size

            color: "#88FF00FF"

            MouseArea {
                anchors.fill: parent
                propagateComposedEvents: true
                onClicked: function(mouse) {
                    console.log("marked clicked", JSON.stringify(item.marker))
                    //mouse.accepted = false
                    //connectorRegister.addEvent(Globals.selectedRail, root.railId, index)
                }
            }
        }
    }
}
