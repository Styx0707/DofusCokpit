on(construct){
   while(true)
   {
      if(!(0x30D1610E | 0x30D1610E))
      {
         if(!ord("\x03"))
         {
            break;
         }
      }
      else
      {
         §§push("\x16\x18\x14");
         §§push(false);
      }
      set(§§pop(),§§pop());
      §§push("contentPath");
      §§push("UI_PopupHexaContent");
      break;
   }
   set(§§pop(),§§pop());
   enabled = true;
   set("\x18\f\t",false);
   styleName = "LightBrownWindowPopup";
   title = "";
}
