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

    Row {
        anchors.top: parent.top
        anchors.topMargin: 50
        anchors.right: parent.right
        anchors.rightMargin: 20

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

    function findRotationPoint(sibling) {
        let rotationPoint = Qt.point(sibling.width - sibling.topOffsetX, 0)
        return sibling.mapToItem(area, rotationPoint)
    }

    function calcXY(index) {
        const radius = 520//1330

        let x = radius * Math.sin(index / 8 * Math.PI)
        let y = radius * Math.cos(index / 8 * Math.PI)

        return {x, y}
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

    function createTrackPiece(sibling, transformation) {
        const track = trackBySelection()
        const rotation = (sibling ? sibling.angle : 0) - 22.5 * transformation.angle

        var component = Qt.createComponent(track);
        var sprite = component.createObject(area);

        sprite.angle = rotation

        if (sibling) {
            const up = (transformation.dir === Globals.dir.up)
            const index = up ? 1 : 0

            let origin = sibling.mapToItem(area, transformation.point)

            sprite.originX = sprite.rotationData[index].point.x
            sprite.originY = sprite.rotationData[index].point.y

            sprite.topVisible = up
            sprite.bottomVisible = !up

            sprite.x = origin.x - (up ? sprite.width : sprite.rotationData[0].point.x)
            sprite.y = origin.y - (up ? sprite.height : 0)

            let angle = sprite.rotationData[index].angle
            sprite.angle += angle ? 22.5 : 0
        }

        sprite["add"].connect (function (transformation) {
            createTrackPiece(sprite, transformation)
        })
    }

    Component.onCompleted: {
        root.trackType = Globals.rail.switchRail
        root.createTrackPiece(undefined, {angle: 0, dir: 1})
        root.trackType = Globals.rail.straight
    }

    Item {
        id: area
        // x: 400
        y: -375
        height: parent.height
        width: parent.width
        scale: 0.5

        // GridView {
        //     id: grid

        //     property real size: 40

        //     z: -1
        //     anchors.fill: parent
        //     cellHeight: grid.size
        //     cellWidth: grid.size
        //     model: 4096
        //     delegate: Rectangle {
        //         width: grid.cellWidth
        //         height: grid.cellHeight
        //         color: "transparent"
        //         border.width: 1
        //     }

        // }

        // Rectangle {
        //     id: p1
        //     x: -20
        //     y: -20
        //     z: 5
        //     height: 40
        //     width: 40
        //     radius: 20
        //     color: "gold"
        //     opacity: 0.5
        // }

        Behavior on scale {
            NumberAnimation { duration: area.scale > 1.5 ? 150 : 250 }
        }
    }
}
