import QtQuick
import QtQuick.Controls

Column {
    id: root
    property int trackType: Rail.Straight

    Row {
        Button {
            text: "Save"
            onClicked: rails.save()
        }

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
            checked: root.trackType === Rail.SwitchLeft
            checkable: true
            text: "Switch Left"
            onClicked: root.trackType = Rail.SwitchLeft
        }

        Button {
            checked: root.trackType === Rail.SwitchRight
            checkable: true
            text: "Switch Right"
            onClicked: root.trackType = Rail.SwitchRight
        }
    }
}
