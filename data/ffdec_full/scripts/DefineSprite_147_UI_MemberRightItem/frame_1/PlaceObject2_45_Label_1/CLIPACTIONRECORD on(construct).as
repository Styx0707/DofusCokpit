on(construct){
   while(true)
   {
      if(!ord("\t"))
      {
         if(!ord("\t"))
         {
            break;
         }
      }
      else
      {
         §§push("\x0b");
      }
      if(ord(§§pop()))
      {
         enabled = true;
         html = false;
         multiline = false;
         styleName = "BrownLeftMediumLabel";
         §§push("text");
         §§push("");
         if(!getTimer())
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            §§goto(addr1fc2d);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   wordWrap = false;
   addr1fc2d:
}
