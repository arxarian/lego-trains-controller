import QtQuick
import QtQuick.Controls

Item {
    id: root

    property real scaleFactor: 0.2
    property real minimalScale: 0.1
    property real maximalScale: 3

    property int trackType: 0

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

    function pointOnCircle(sibling, anticlockwise = true) {
        // notes: y ax is reversed!
        // * so the 0 rotation equals to 90 degrees
        // * for x ax is used sinus
        // * for y ax is used cosinus

        const radius = 1358
        const basicAngleIncrement = 22.5
        const defaultRotation = 90

        // find the center
        let angleRadius = Math.PI / 8 * ((-sibling.rotation + defaultRotation) / basicAngleIncrement)
        let cx = sibling.x + sibling.width - radius * Math.sin(angleRadius)
        let cy = sibling.y + sibling.height - radius * Math.cos(angleRadius)

        console.log("p", sibling.x + sibling.width, sibling.y + sibling.height, -sibling.rotation + defaultRotation)
        console.log("center", cx, cy)

        // find the next point
        angleRadius = Math.PI / 8 * ((-sibling.rotation + basicAngleIncrement * (anticlockwise ? 1 : -1)
                                      + defaultRotation) / basicAngleIncrement)
        let x = cx + radius * Math.sin(angleRadius)
        let y = cy + radius * Math.cos(angleRadius)

        console.log("p next", x, y)

        return {x, y}
    }

    function createCurvedTrackPiece(sibling, transformation) {

        let rotation = (sibling ? sibling.rotation : 0) - 22.5 * transformation.angle
        let x = sibling ? sibling.x : 0
        let y = sibling ? sibling.y : 0

        let component = Qt.createComponent("CurvedTrackPiece.qml");
        let sprite = component.createObject(area);

        if (sibling) {
            console.log("sibling type", sibling.trackType)
            if (sibling.trackType === 1) {
                if (transformation.dir > 0) {
                    let p = pointOnCircle(sibling, true)
                    sprite.x = p.x - sprite.width
                    // + sprite.bottomOffsetX - sibling.topOffsetX  // connects curved to straight
                    sprite.y = p.y - sprite.height
                    sprite.bottomVisible = false
                } else {
                    let p = pointOnCircle(sibling, false)
                    sprite.x = p.x - sprite.width
                    sprite.y = p.y - sprite.height
                    sprite.topVisible = false
                    rotation += 22.5
                }
            } else if (sibling.trackType === 0) {
                if (transformation.dir > 0) {
                    sprite.x -= sprite.bottomOffsetX
                    sprite.y -= sprite.height
                }
            }
        }

        sprite.transformOrigin = Item.BottomRight
        sprite.rotation = rotation

        sprite["add"].connect (function (transformation) {
            createTrackPiece(sprite, transformation)
        })

        return sprite
    }

    Component.onCompleted: {
        root.trackType = 0
        root.createTrackPiece(undefined, {angle: 0, dir: 1})
        root.trackType = 1
    }

    Item {
        id: area
        x: 400
        y: 200
        height: parent.height
        width: parent.width
        scale: 0.5

        Behavior on scale {
            NumberAnimation { duration: area.scale > 1.5 ? 150 : 250 }
        }
    }
}
