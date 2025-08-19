import QtQuick
import QtQuick.Controls

Item {
    id: root

    property real scaleFactor: 0.2
    property real minimalScale: 0.1
    property real maximalScale: 3

    property int trackType: Rail.Straight

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
    }

    Column {
        anchors.top: parent.top
        anchors.topMargin: -24
        anchors.right: parent.right
        anchors.rightMargin: 20
        z: 1

        Row {
            CheckBox {
                text: "Grid"
                checked: Globals.gridVisible
                onClicked: Globals.gridVisible = checked
            }

            CheckBox {
                text: "Track Frame"
                checked: Globals.trackFrameVisible
                onClicked: Globals.trackFrameVisible = checked
            }

            CheckBox {
                text: "Rotation Points"
                checked: Globals.rotationPointsVisible
                onClicked: Globals.rotationPointsVisible = checked
            }
        }

        Row {
            Button {
                checked: root.trackType === Rail.Straight
                checkable: true
                text: "Straight"
                onClicked: root.trackType = Rail.Straight
            }

            Button {
                checked: root.trackType === Rail.Curved
                checkable: true
                text: "Curved"
                onClicked: root.trackType = Rail.Curved
            }

            Button {
                checked: root.trackType === Rail.Switch
                checkable: true
                text: "Switch"
                onClicked: root.trackType = Rail.Switch
            }
        }
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

    function createTrackPiece(sibling, fromIndex = 0) {
        let rail = rails.createRail(root.trackType, sibling, fromIndex)

        var component = Qt.createComponent(rail.source())
        var sprite = component.createObject(area, {railData: rail})

        sprite.connectToSibling()
    }

    Component.onCompleted: {
        root.trackType = Rail.Straight
        root.createTrackPiece()
        root.trackType = Rail.Switch
    }

    Item {
        id: area
        height: parent.height
        width: parent.width
        scale: 0.3

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

        Shortcut {
            enabled: Globals.selectedTrack
            sequences: ["F"]
            onActivated: Globals.selectedTrack.flip()
        }


        Behavior on scale {
            NumberAnimation { duration: area.scale > 1.5 ? 150 : 250 }
        }
    }
}
