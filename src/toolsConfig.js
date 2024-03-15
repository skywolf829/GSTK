// toolConfig.js
// This file exports a configuration for all the windows in the app

import RemovePointsTool from "./components/EditTools/RemovePointsTool"
import AddPointsTool from "./components/EditTools/AddPointsTool"
import {  faCircleMinus, faCirclePlus
  } from '@fortawesome/free-solid-svg-icons';


export const toolsConfig = [
    {
        title: <span>Remove points</span>,
        key: 'removePoints',
        tooltip: 'Delete selected gaussians',
        component: RemovePointsTool,
        icon: faCircleMinus,
        minWidth: 300,
        minHeight: 150
    },
    {
        title: <span>Add points</span>,
        key: 'addPoints',
        tooltip: 'Create new gaussians',
        component: AddPointsTool,
        icon: faCirclePlus,
        minWidth: 300,
        minHeight: 150
      },
  ];