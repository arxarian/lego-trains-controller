import QtQuick
import TrainView

Rectangle {
    visible: Globals.rotationPointsVisible

    z: 1
    width: 20
    height: 20
    radius: width
    opacity: 0.8
    color: "red"
    
    Rectangle {
        anchors.centerIn: parent
        width: 2
        height: 2
        color: "black"
    }
}
