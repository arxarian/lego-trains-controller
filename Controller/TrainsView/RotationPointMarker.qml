import QtQuick
import TrainsView

Rectangle {
    z: 1
    width: 20
    height: 20
    radius: width
    opacity: 0.8
    color: "gold"
    
    Rectangle {
        anchors.centerIn: parent
        width: 2
        height: 2
        color: "black"
    }
}
