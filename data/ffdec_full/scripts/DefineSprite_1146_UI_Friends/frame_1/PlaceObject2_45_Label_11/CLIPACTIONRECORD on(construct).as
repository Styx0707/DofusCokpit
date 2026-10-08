on(construct){
   while(true)
   {
      if(!(0x08AAED5E | 0x08AAED5E))
      {
         if(!ord("\x04"))
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
            §§goto(addr376bd);
         }
      }
      set(§§pop(),§§pop());
      §§push("wordWrap");
      §§push(false);
      break;
   }
   set(§§pop(),§§pop());
   addr376bd:
}
