import QtQuick
import TrainView

Item {
    id: item

    property Marker marker

    x: item.marker.rotator.x
    y: item.marker.rotator.y

    SelectableItem {
        id: selectableItem

        deleteAction: function() {item.marker.remove()}

        anchors.centerIn: parent
        width: 160
        height: 80
        enabled: Globals.editMode && item.marker.visible
        rotation: item.marker.rotator.angle

        Rectangle {
            id: markerBrick
            anchors.fill: parent

            visible: item.marker.visible
            color: item.marker.color

            onVisibleChanged: { if (visible) {
                    selectableItem.forceActiveFocus()
                } else {
                    item.forceActiveFocus()
                }
            }
        }

        Rectangle {
            id: markerPoint

            property real size: 30
            readonly property real centerOffset: size / 2

            function updatePosition() {
                item.marker.position = mapToItem(Globals.globalArea, centerOffset, centerOffset)
            }

            anchors.centerIn: parent
            visible: Globals.editMode && (markerTypes ? markerTypes.markersActive : true) && !item.marker.visible && item.marker.enabled

            radius: markerPoint.size
            width: markerPoint.size
            height: markerPoint.size

            color: "#88FF00FF"

            onXChanged: updatePosition()
            onYChanged: updatePosition()

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
