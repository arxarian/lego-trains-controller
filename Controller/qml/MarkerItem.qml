import QtQuick
import TrainView

Item {
    id: item

    property Marker marker

    x: item.marker.rotator.x
    y: item.marker.rotator.y

    SelectableItem {
        id: selectableItem

        deleteAction: function() {
            console.log("wanna delete")
        }

        propagateComposedEvents: !item.marker.visible

        anchors.centerIn: parent
        width: 160
        height: 80
        rotation: item.marker.rotator.angle

        Rectangle {
            id: markerBrick
            anchors.fill: parent

            visible: item.marker.visible
            color: item.marker.color

            onVisibleChanged: { if (visible) {
                    selectableItem.forceActiveFocus()
                }
            }
        }

        Rectangle {
            id: markerPoint

            property real size: 50

            anchors.centerIn: parent
            visible: (markerTypes ? markerTypes.markersActive : true) && !item.marker.visible

            radius: markerPoint.size
            width: markerPoint.size
            height: markerPoint.size

            color: "#88FF00FF"

            MouseArea {
                anchors.fill: parent
                propagateComposedEvents: true
                onClicked: function(mouse) {
                    if (Globals.selectedMarker >= 0) {
                        item.marker.color = markerTypes.get(Globals.selectedMarker).color
                        item.marker.visible = true
                    } else {
                        console.warn("Marker was not found, Globals.selectedMarker equals to",
                                     Globals.selectedMarker)
                    }
                }
            }
        }
    }
}
