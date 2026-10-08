on(construct){
   while(true)
   {
      if(!ord("\x04"))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x04");
      }
      if(ord(§§pop()))
      {
         set("\x16\x18\x14",false);
         contentPath = "none";
         enabled = true;
         set("\x18\f\t",false);
         §§push("styleName");
         §§push("LightBrownWindow");
         if(!getTimer())
         {
            §§goto(addr10b02);
         }
      }
      set(§§pop(),§§pop());
      title = "";
      break;
   }
   addr10b02:
   new §\§\§pop()§();
}
