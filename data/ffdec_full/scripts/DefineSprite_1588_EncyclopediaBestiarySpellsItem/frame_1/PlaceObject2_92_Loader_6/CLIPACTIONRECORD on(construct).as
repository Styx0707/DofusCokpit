on(construct){
   while(true)
   {
      if(!ord("\x05"))
      {
         if(!ord("\x05"))
         {
            break;
         }
      }
      else
      {
         §§push("\x07");
      }
      if(ord(§§pop()))
      {
         autoLoad = true;
         centerContent = false;
         contentPath = "IconRangeBoostable";
         enabled = true;
         §§push("fallbackContentPath");
         §§push("");
         if(!(getTimer() + 1))
         {
            §§pop() extends §§pop();
            §§goto(addrbee8);
         }
      }
      set(§§pop(),§§pop());
      forceReload = false;
      break;
   }
   scaleContent = true;
   styleName = "default";
   addrbee8:
}
