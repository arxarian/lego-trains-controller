import QtQuick
import QtQuick.Controls

Item {
    id: root

    property real scaleFactor: 0.2
    property real minimalScale: 0.1
    property real maximalScale: 3

    MouseArea {
        id: mouseArea

        property real offsetX: 0
        property real offsetY: 0
        property real startX: 0
        property real startY: 0

        anchors.fill: parent
        onPressed: (mouse) => {
            mouseArea.startX = area.x
            mouseArea.startY = area.y
            mouseArea.offsetX = mouse.x
            mouseArea.offsetY = mouse.y
        }
        onPositionChanged: (mouse) => {
            area.x = mouse.x - mouseArea.offsetX + mouseArea.startX
            area.y = mouse.y - mouseArea.offsetY + mouseArea.startY
        }

        onClicked: {
            if (rails.rowCount() === 0) {
                rails.append(Globals.selectedType)
            }
        }
    }

    ControlPanel {
        anchors.right: parent.right
        anchors.rightMargin: 20
        anchors.top: parent.top
        anchors.topMargin: -24
        z: 1
    }

    WheelHandler {
        id: wheel
        onWheel: (event) => {
            if (event.angleDelta.y > 0) {
                area.scale = Math.min(maximalScale, area.scale + scaleFactor)
            } else {
                area.scale = Math.max(minimalScale, area.scale - scaleFactor)
            }
        }
    }

    Item {
        id: area
        height: parent.height
        width: parent.width
        scale: 0.3

        Repeater {
            model: rails
            delegate: TrackPiece {
                id: rail
                railData: model.object
                Component.onCompleted: {
                    rails.registerRail(rail, rail.railData.id)
                    // rail.connectToSibling() - TODO - it's need for repositioning!
                }
            }
        }

        GridView {
            id: grid

            property real size: 40

            z: -1
            anchors.fill: parent
            anchors.margins: -15 * grid.size
            visible: Globals.gridVisible
            cellHeight: grid.size
            cellWidth: grid.size
            interactive: false
            model: 4096
            delegate: Rectangle {
                width: grid.cellWidth
                height: grid.cellHeight
                color: "transparent"
                border.width: 2
            }
        }

        Shortcut {
            enabled: Globals.selectedTrack
            sequences: ["R"]
            onActivated: Globals.selectedTrack.rotate()
        }

        Behavior on scale {
            NumberAnimation { duration: area.scale > 1.5 ? 150 : 250 }
        }
    }
}
