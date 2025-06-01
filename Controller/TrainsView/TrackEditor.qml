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



        // console.log("rotation", rotation / -22.5, transformation.angle, sprite.height)
        if (sibling) {
            // calc the center
            let r = 1361
            let px = x + sprite.width// - r   // just for now
            let py = y + sprite.height

            let p = rotatePoint(px, py, px - r, py, rotation)

            // console.log(point_on_circle(r, ))

            console.log("new point", p.x, p.y)
            sprite.x = p.x - sprite.width
            sprite.y = p.y - sprite.height
            sprite.bottomVisible = false
            sibling.topVisible = false

            // let sin = Math.sin(Math.PI / 8 * (rotation / -22.5))
            // let cos = Math.cos(Math.PI / 8 * (rotation / -22.5))

            // sprite.rotation += 22.5
            // rotation += 22.5
            // radius 1361
            // if (transformation.dir > 0) {
            //     sprite.x -= (r/*sprite.height/* - sibling.topOffsetX*/) * Math.sin(Math.PI / 8 * (rotation / -22.5))
            //             // + -transformation.offsetX
            //             // + sibling.topOffsetX
            //             // + sprite.bottomOffsetX - sibling.topOffsetX  // connects curved to straight
            //     sprite.y -= (r/*sprite.height/* - sibling.topOffsetX*/) * Math.cos(Math.PI / 8 * (rotation / -22.5))
            //     sprite.bottomVisible = false
            // } else {
            //     sprite.topVisible = false
            // }
        }

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
        for (let i = 0; i < 2; i++) {
            sibling = root.createCurvedTrackPiece(sibling, {angle: 0, dir: 1})
        }
    }

    Item {
        id: area
        x: 200
        y: 200
        height: parent.height
        width: parent.width
        scale: 0.4

        Behavior on scale {
            NumberAnimation { duration: area.scale > 1.5 ? 150 : 250 }
        }
    }
}
