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
      key: 'serverConnection',
      component: ServerConnection,
      title: 'Server Connection',
      icon: faPlug,
      tooltip: 'Connect to server'
    },
    {
      key: 'trainer',
      component: Trainer,
      title: 'Trainer',
      icon: faPlayCircle,
      tooltip: 'Training window'
    },    
    {
      key: 'datasetSetup',
      component: DatasetSetup,
      title: 'Dataset setup',
      icon: faDatabase,
      tooltip: 'Dataset loading'
    },   
    {
      key: 'trainerSettings',
      component: TrainerSettings,
      title: 'Trainer Settings',
      icon: faSlidersH,
      tooltip: 'Trainer settings'
    },     
    {
      key: 'rendererSettings',
      component: RenderSettings,
      title: 'Render Settings',
      icon: faDesktop,
      tooltip: 'Render settings'
    }, 
    {
      key: 'toolbar',
      component: Toolbar,
      title: 'Toolbar',
      icon: faHammer,
      tooltip: 'Edit tools'
    }
  ];