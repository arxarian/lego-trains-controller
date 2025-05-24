import QtQuick

Item {
    id: root

    property real scaleFactor: 0.2
    property real minimalScale: 0.05
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

    function createStraightTrackPiece(sibling, dir) {
        var component = Qt.createComponent("StraightTrackPiece.qml");
        var sprite = component.createObject(area, {x: 0, y: 0});

        sprite["add"].connect (function (dir) {
            createStraightTrackPiece(sprite, dir)
        })

        if (sibling) {
            if (dir === "left") {
                sprite.x = sibling.x - sibling.width
                sprite.rightVisible = false
            } else {
                sprite.x = sibling.x + sibling.width
                sprite.leftVisible = false
            }
        }
    }

    function calcXY(index, radius) {
        let x = radius * Math.cos(-index / 8 * Math.PI)
        let y = radius * Math.sin(-index / 8 * Math.PI)
        return {x, y}
    }

    function createCurvedTrackPiece(sibling, dir) {
        let component = Qt.createComponent("CurvedTrackPiece.qml");
        let radius = 1330
        for (let i = 0; i < 16; i++) {
                let p = calcXY(i, radius)
                let sprite = component.createObject(area, {
                    x: p.x,
                    y: p.y,
                    rotation: i * -22.5
                });
                sprite.transformOrigin = Item.BottomRight
            }
    }
        // let index = sibling ? (Math.abs(sibling.rotation) / 22.5 + 1) : 0
        // let angle = index * -22.5
        // let radius = 704
        // let p = calcXY(index, radius)
        // let sprite = component.createObject(area, {x: p.x, y: p.y});
        // sprite.transformOrigin = Item.BottomLeft
        // sprite.rotation = angle

        // sprite["add"].connect (function (dir) {
        //     createCurvedTrackPiece(sprite, dir)
        // })
    // }

    Component.onCompleted: root.createCurvedTrackPiece()

    Item {
        id: area
        height: parent.height
        width: parent.width
        scale: 0.3

        // Canvas {
        //     anchors.fill: parent
        //     onPaint: {
        //         var ctx = getContext("2d");
        //         ctx.beginPath();
        //         ctx.fillStyle = Qt.rgba(1, 0, 0, 0.5);
        //         ctx.ellipse(0, 0, 352 * 3, 352 * 3)
        //         ctx.fill();
        //     }
        // }
    }
}
