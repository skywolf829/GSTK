// windowsConfig.js
// This file exports a configuration for all the windows in the app
import ExampleWindow from "../components/ExampleWindow";
import ServerConnection from "../components/ServerConnection";
import TrainerSettings from "../components/TrainerSettings";
import Toolbar from "../components/Toolbar";
import DatasetSetup from "../components/DatasetSetup";
import Trainer from "../components/Trainer";
import RenderSettings from "../components/RenderSettings";


import { faPaintBrush, faCog, faPlug ,
  faSlidersH, faCogs, faBrain, 
  faChartLine, faNetworkWired,
  faHammer, faDatabase, faFileImport, faFile, faFolderOpen,
  faPlayCircle, faRobot, faDesktop, faScrewdriver
  } from '@fortawesome/free-solid-svg-icons';


export const windowsConfig = [
    {
      title: <span>Server Connection</span>,
      key: 'serverConnection',
      tooltip: 'Connect to server',
      component: ServerConnection,
      icon: faPlug,
      minWidth: 220,
      minHeight: 125
    },
    {
      title: <span>Trainer</span>,
      key: 'trainer',
      tooltip: 'Training window',
      component: Trainer,
      icon: faPlayCircle,
      minWidth: 240,
      minHeight: 150
    },    
    {
      title: <span>Dataset setup</span>,
      key: 'datasetSetup',
      tooltip: 'Dataset loading',
      component: DatasetSetup,
      icon: faDatabase,
      minWidth: 270,
      minHeight: 170
    },   
    {
      title: <span>Trainer Settings</span>,
      key: 'trainerSettings',
      tooltip: 'Trainer settings',
      component: TrainerSettings,
      icon: faSlidersH,
      minWidth: 370,
      minHeight: 490
    },     
    {
      title: <span>Render Settings</span>,
      key: 'rendererSettings',
      tooltip: 'Render settings',
      component: RenderSettings,
      icon: faDesktop,
      minWidth: 350,
      minHeight: 210
    }, 
    {
      key: 'toolbar',
      component: Toolbar,
      title: 'Toolbar',
      icon: faHammer,
      tooltip: 'Edit tools',
      minWidth: 240,
      minHeight: 135
    }
  ];