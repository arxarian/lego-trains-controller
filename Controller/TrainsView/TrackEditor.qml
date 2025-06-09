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

    function createTrackPiece(sibling, transformation) {
        if (root.trackType === Globals.rail.straight) {
            createStraightTrackPiece(sibling, transformation)
        } else if (root.trackType === Globals.rail.curved) {
            createCurvedTrackPiece(sibling, transformation)
        } else if (root.trackType === Globals.rail.switchRail) {
            createSwitchTrackPiece(sibling, transformation)
        }
    }

    function createStraightTrackPiece(sibling, transformation) {
        let rotation = (sibling ? sibling.rotation : 0) - 22.5 * transformation.angle
        let x = sibling ? sibling.x : 0
        let y = sibling ? sibling.y : 0

        var component = Qt.createComponent("StraightTrackPiece.qml");
        var sprite = component.createObject(area, {x: x, y: y, rotation: rotation});
        sprite.transformOrigin = transformation.rotationOrigin ? transformation.rotationOrigin : Item.BottomRight

        if (sibling) {
            if (sibling.trackType === Globals.rail.curved) {
                if (transformation.dir === Globals.dir.up) {
                    let rotationPoint = findRotationPoint(sibling)
                    sprite.x = rotationPoint.x - sprite.width
                    sprite.y = rotationPoint.y - sprite.height
                    sprite.bottomVisible = false
                } else if (transformation.dir === Globals.dir.down) {
                    //
                }
            } else if (sibling.trackType === Globals.rail.straight) {
                let rotationPoint = Qt.point(transformation.offsetX, transformation.offsetY)
                let origin = sibling.mapToItem(area, rotationPoint)

                sprite.x = origin.x - sprite.width
                sprite.y = origin.y - (transformation.dir === Globals.dir.up ? sprite.height : 0)

                sprite.topVisible = (transformation.dir === Globals.dir.up)
                sprite.bottomVisible = (transformation.dir === Globals.dir.down)
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

    function pointOnCircle(sibling, radius, anticlockwise = true) {
        // notes: y ax is reversed!
        // * so the 0 rotation equals to 90 degrees
        // * for x ax is used sinus
        // * for y ax is used cosinus

        // find the center
        let angleRadius = Math.PI / 8 * ((-sibling.rotation + Globals.defaultRotation) / Globals.basicAngleIncrement)
        let cx = sibling.x + sibling.width - radius * Math.sin(angleRadius)
        let cy = sibling.y + sibling.height - radius * Math.cos(angleRadius)

        console.log("p", sibling.x + sibling.width, sibling.y + sibling.height, -sibling.rotation + Globals.defaultRotation)
        console.log("center", cx, cy)

        // find the next point
        angleRadius = Math.PI / 8 * ((-sibling.rotation + Globals.basicAngleIncrement * (anticlockwise ? 1 : -1)
                                      + Globals.defaultRotation) / Globals.basicAngleIncrement)
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
            if (sibling.trackType === Globals.rail.straight) {
                if (transformation.dir === Globals.dir.up) {
                    let rotationPoint = findRotationPoint(sibling)
                    sprite.x = rotationPoint.x - sprite.width
                    sprite.y = rotationPoint.y - sprite.height
                    sprite.bottomVisible = false
                } else if (transformation.dir === Globals.dir.down) {
                    //
                }
            } else if (sibling.trackType === Globals.rail.curved) {
                if (transformation.dir === Globals.dir.up) {
                    let rotationPoint = findRotationPoint(sibling)
                    sprite.x = rotationPoint.x - sprite.width
                    sprite.y = rotationPoint.y - sprite.height
                    sprite.bottomVisible = false
                } else if (transformation.dir === Globals.dir.down) {
                    let p = pointOnCircle(sibling, Globals.curveRadius, false)
                    sprite.x = p.x - sprite.width
                    sprite.y = p.y - sprite.height
                    sprite.topVisible = false
                    rotation += 22.5
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
        root.trackType = Globals.rail.straight
        root.createTrackPiece(undefined, {angle: 0, dir: 1})
        // root.trackType = Globals.rail.curved
    }

    Item {
        id: area
        x: 400
        y: 200
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
