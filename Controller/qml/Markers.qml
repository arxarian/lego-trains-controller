import QtQuick
import TrainView

Item
{
    id: root

    property var model

    visible: markerTypes.markersActive

    Repeater {
        model: root.model
        delegate: Item {
            id: item

            property Marker marker: model.object

            Rectangle {

                id: markerBrick
                visible: item.marker.visible
                rotation: item.marker.rotator.angle
                anchors.centerIn: markerPoint
                color: item.marker.color
                width: 160
                height: 80
            }

            Rectangle {
                id: markerPoint

                property real size: 50

                visible: !item.marker.visible
                x: item.marker.rotator.x - markerPoint.size / 2
                y: item.marker.rotator.y - markerPoint.size / 2
                rotation: item.marker.rotator.angle

                radius: markerPoint.size
                width: markerPoint.size
                height: markerPoint.size

                color: "#88FF00FF"

                MouseArea {
                    anchors.fill: parent
                    propagateComposedEvents: true
                    onClicked: function(mouse) {
                        item.marker.color = markerTypes.get(Globals.selectedMarker).color
                        item.marker.visible = true
                    }
                }
            }
        }
    }
}
