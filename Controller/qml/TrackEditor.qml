import QtQuick
import QtQuick.Controls

Item {
    id: root

    readonly property real scaleFactor: 0.05
    readonly property real minimalScale: 0.05
    readonly property real maximalScale: 0.4
    readonly property bool animationEnabled: !mouseArea.pressed

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
            settings.canvas_x = mouse.x - mouseArea.offsetX + mouseArea.startX
            settings.canvas_y = mouse.y - mouseArea.offsetY + mouseArea.startY
        }

        onClicked: {
            if (rails.rowCount() === 0) {
                connectorRegister.addEvent(Globals.selectedRail)
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
                settings.canvas_zoom = Math.min(maximalScale, area.scale + scaleFactor)
            } else {
                settings.canvas_zoom = Math.max(minimalScale, area.scale - scaleFactor)
            }
        }
    }

    Item {
        id: area
        x: settings ? settings.canvas_x : 0
        y: settings ? settings.canvas_y : 0
        height: parent.height
        width: parent.width
        scale: settings ? settings.canvas_zoom : 1

        Repeater {
            model: rails
            delegate: TrackPiece {
                railData: model.object
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

        Behavior on scale {
            enabled: root.animationEnabled
            NumberAnimation { duration: area.scale > 0.25 ? 150 : 250 }
        }

        Behavior on x {
            enabled: root.animationEnabled
            NumberAnimation { duration: 250 }
        }

        Behavior on y {
            enabled: root.animationEnabled
            NumberAnimation { duration: 250 }
        }
    }
}
