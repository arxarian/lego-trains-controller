import QtQuick
import QtQuick.Controls

Item {
    id: root

    property real scaleFactor: 0.2
    property real minimalScale: 0.1
    property real maximalScale: 3

    property int trackType: 1

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
            checked: root.trackType === 0
            checkable: true
            text: "Straight"
            onClicked: root.trackType = 0
        }

        Button {
            checked: root.trackType === 1
            checkable: true
            text: "Curved"
            onClicked: root.trackType = 1
        }

        Button {
            checked: root.trackType === 2
            checkable: true
            text: "Switch"
            onClicked: root.trackType = 2
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

    function calcXY(index) {
        const radius = 520//1330

        let x = radius * Math.sin(index / 8 * Math.PI)
        let y = radius * Math.cos(index / 8 * Math.PI)

        return {x, y}
    }

    function createTrackPiece(sibling, transformation) {
        if (root.trackType === 0) {
            createStraightTrackPiece(sibling, transformation)
        } else if (root.trackType === 1) {
            createCurvedTrackPiece(sibling, transformation)
        } else if (root.trackType === 2) {
            createSwitchTrackPiece(sibling, transformation)
        }
    }

    function createStraightTrackPiece(sibling, transformation) {
        let rotation = (sibling ? sibling.rotation : 0) - 22.5 * transformation.angle
        let x = sibling ? sibling.x : 0
        let y = sibling ? sibling.y : 0

        var component = Qt.createComponent("StraightTrackPiece.qml");
        var sprite = component.createObject(area, {x: x, y: y, rotation: rotation});
        sprite.transformOrigin = Item.BottomRight

        if (sibling) {
            if (transformation.dir > 0) {
                sprite.x -= sprite.height * Math.sin(Math.PI / 8 * (rotation / -22.5))
                sprite.y -= sprite.height * Math.cos(Math.PI / 8 * (rotation / -22.5))
                sprite.bottomVisible = false
            } else {
                sprite.x += sprite.height * Math.sin(Math.PI / 8 * (rotation / -22.5))
                sprite.y += sprite.height * Math.cos(Math.PI / 8 * (rotation / -22.5))
                sprite.topVisible = false
            }
        }

        sprite["add"].connect (function (transformation) {
            createTrackPiece(sprite, transformation)
        })
    }

    function createSwitchTrackPiece(sibling, transformation) {
        let index = (sibling ? (Math.abs(sibling.rotation) / 22.5) : 0) * transformation.angle
        let rotation = sibling ? sibling.rotation : 0
        let p = calcXY(index)

        var component = Qt.createComponent("SwitchTrackPiece.qml");
        var sprite = component.createObject(area, {x: p.x, y: p.y, rotation: rotation});

        sprite["add"].connect (function (transformation) {
            createTrackPiece(sprite, transformation)
        })

        if (sibling) {
            if (transformation.angle === 1) {
                sprite.y = sibling.y - sprite.height
                sprite.bottomVisible = false
            } else if (transformation.angle === 2 ) {
                sprite.y = sibling.y - sprite.height
                sprite.bottomVisible = false
            } else if (transformation.angle === -1) {
                sprite.y = sibling.y + sibling.height
                sprite.topRightVisible = false
            }
        }
    }

    // working
    function rotatePoint(x, y, cx, cy, angleDeg) {
        let angleRad = angleDeg * Math.PI / 180

        console.log("center", cx, cy)

        let dx = x - cx
        let dy = y - cy

        let rx = dx * Math.cos(angleRad) - dy * Math.sin(angleRad)
        let ry = dx * Math.sin(angleRad) + dy * Math.cos(angleRad)

        return {
            x: cx + rx,
            y: cy + ry
        }
    }

    function point_on_circle(radius, initial_angle_deg, delta_angle_deg) {
        let angleRad = (initial_angle_deg + delta_angle_deg) * Math.PI / 180
        x = radius * Math.cos(angleRad)
        y = radius * Math.sin(angleRad)
        return {x, y}
    }

    function createCurvedTrackPiece(sibling, transformation) {

        if (sibling) transformation.angle = 1

        let rotation = (sibling ? sibling.rotation : 0) - 22.5 * transformation.angle
        let x = sibling ? sibling.x : 0
        let y = sibling ? sibling.y : 0

        let component = Qt.createComponent("CurvedTrackPiece.qml");
        let sprite = component.createObject(area, { x: x, y: y, rotation: rotation });
        sprite.transformOrigin = Item.BottomRight


        // find the center
        let r = 1361
        let angle_r = Math.PI / 8 * (90 / 22.5)
        let cx = sprite.width - r * Math.sin(angle_r)
        let cy = sprite.height - r * Math.cos(angle_r)
        console.log("x1, y1", sprite.width, sprite.height)
        console.log("cx, cy", cx, cy)
        center.x = cx
        center.y = cy

        angle_r = Math.PI / 8 * (112.5 / 22.5)
        let x2 = cx + r * Math.sin(angle_r)
        let y2 = cy + r * Math.cos(angle_r)
        console.log("x2, y2", x2.toFixed(1), y2.toFixed(1))
        p2.x = x2 - p2.width / 2
        p2.y = y2 - p2.height / 2

        angle_r = Math.PI / 8 * (135 / 22.5)
        let x3 = cx + r * Math.sin(angle_r)
        let y3 = cy + r * Math.cos(angle_r)
        console.log("x3, y3", x3.toFixed(1), y3.toFixed(1))
        p3.x = x3 - p3.width / 2
        p3.y = y3 - p3.height / 2


        // console.log("rotation", rotation / -22.5, transformation.angle, sprite.height)
        // if (sibling) {
        //     // calc the center
        //     let r = 1361
        //     let p1x = x + sprite.width
        //     let p1y = y + sprite.height

        //     let p2 = rotatePoint(p1x, p1y, p1x - r, p1y, rotation)

        //     // console.log(point_on_circle(r, ))

        //     console.log("new point", p2.x, p2.y)
        //     sprite.x = p2.x - sprite.width
        //     sprite.y = p2.y - sprite.height
        //     sprite.bottomVisible = false
        //     sibling.topVisible = false


        //     // sprite.rotation += 22.5
        //     // rotation += 22.5
        //     // radius 1361
        //     // if (transformation.dir > 0) {
        //     //     sprite.x -= (r/*sprite.height/* - sibling.topOffsetX*/) * Math.sin(Math.PI / 8 * (rotation / -22.5))
        //     //             // + -transformation.offsetX
        //     //             // + sibling.topOffsetX
        //     //             // + sprite.bottomOffsetX - sibling.topOffsetX  // connects curved to straight
        //     //     sprite.y -= (r/*sprite.height/* - sibling.topOffsetX*/) * Math.cos(Math.PI / 8 * (rotation / -22.5))
        //     //     sprite.bottomVisible = false
        //     // } else {
        //     //     sprite.topVisible = false
        //     // }
        // }

        sprite["add"].connect (function (transformation) {
            createTrackPiece(sprite, transformation)
        })

        console.log("x, y", sprite.x, sprite.y)

        return sprite
    }

    Component.onCompleted: {
//          root.createTrackPiece(undefined, {angle: 0, offsetX: 0, offsetY: 0})
// return
        var sibling = undefined
        for (let i = 0; i < 1; i++) {
            sibling = root.createCurvedTrackPiece(sibling, {angle: 0, dir: 1})
        }
    }

    Item {
        id: area
        x: 200
        y: 200
        height: parent.height
        width: parent.width
        scale: 0.2

        Rectangle {
            id: center
            z: 10
            width: 40
            height: 40
            radius: 20
            color: "green"
        }

        Rectangle {
            id: p2
            z: 10
            width: 40
            height: 40
            radius: 20
            color: "red"
        }

        Rectangle {
            id: p3
            z: 10
            width: 40
            height: 40
            radius: 20
            color: "blue"
        }

        Behavior on scale {
            NumberAnimation { duration: area.scale > 1.5 ? 150 : 250 }
        }
    }
}
