import QtQuick
import QtQuick.Controls

Column {
    id: root

    Row {
        Button {
            text: "Save"
            onClicked: projectStorage.saveProject(project)
        }

        Button {
            text: "Load"
            onClicked: projectStorage.loadProject(project.name)
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
            checked: Globals.selectedType === Rail.Straight
            checkable: true
            text: "Straight"
            onClicked: Globals.selectedType = Rail.Straight
        }

        Button {
            checked: Globals.selectedType === Rail.Curved
            checkable: true
            text: "Curved"
            onClicked: Globals.selectedType = Rail.Curved
        }

        Button {
            checked: Globals.selectedType === Rail.SwitchLeft
            checkable: true
            text: "Switch Left"
            onClicked: Globals.selectedType = Rail.SwitchLeft
        }

        Button {
            checked: Globals.selectedType === Rail.SwitchRight
            checkable: true
            text: "Switch Right"
            onClicked: Globals.selectedType = Rail.SwitchRight
        }
    }
}
