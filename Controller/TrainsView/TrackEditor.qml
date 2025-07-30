import QtQuick
import QtQuick.Controls

Item {
    id: root

    property real scaleFactor: 0.2
    property real minimalScale: 0.1
    property real maximalScale: 3

    property int trackType: Globals.rail.straight

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
                checked: root.trackType === Globals.rail.straight
                checkable: true
                text: "Straight"
                onClicked: root.trackType = Globals.rail.straight
            }

            Button {
                checked: root.trackType === Globals.rail.curved
                checkable: true
                text: "Curved"
                onClicked: root.trackType = Globals.rail.curved
            }

            Button {
                checked: root.trackType === Globals.rail.switchRail
                checkable: true
                text: "Switch"
                onClicked: root.trackType = Globals.rail.switchRail
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

    function trackBySelection() {
        if (root.trackType === Globals.rail.straight) {
            return "StraightTrackPiece.qml"
        } else if (root.trackType === Globals.rail.curved) {
            return "CurvedTrackPiece.qml"
        } else if (root.trackType === Globals.rail.switchRail) {
            return "SwitchTrackPiece.qml"
        }
    }

    function createTrackPiece(sibling, index = 0) { // the index is for sibling, what's the index for the new?
        const track = trackBySelection()
        var component = Qt.createComponent(track)
        var sprite = component.createObject(area)

        sprite.angle = sibling ? sibling.angle : 0

        if (sibling) {
            const transformation = sibling.rotationData[1 - index]
            const up = (transformation.dir === Globals.dir.up)

            let origin = sibling.mapToItem(area, transformation.point)

            sprite.originX = sprite.rotationData[index].point.x
            sprite.originY = sprite.rotationData[index].point.y

            sprite.rotationData[0].visible = false

            sprite.x = origin.x - (up ? sprite.width : sprite.rotationData[1].point.x)
            sprite.y = origin.y - (up ? sprite.height : 0)

            let angle = sprite.rotationData[index].angle - transformation.angle
            sprite.angle += angle * 22.5
        }

        sprite["add"].connect (function (transformation) {
            createTrackPiece(sprite, transformation)
        })
    }

    Component.onCompleted: {
        root.trackType = Globals.rail.straight
        root.createTrackPiece()
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
            enabled: root.selected
            sequences: ["R"]
            onActivated: area.rotation = (area.rotation + 45) % 360
        }

        Behavior on scale {
            NumberAnimation { duration: area.scale > 1.5 ? 150 : 250 }
        }

        Behavior on rotation {
            RotationAnimator {
                id: rotationAninamtion
                direction: RotationAnimation.Clockwise
                duration : 200
            }
        }
    }
}
