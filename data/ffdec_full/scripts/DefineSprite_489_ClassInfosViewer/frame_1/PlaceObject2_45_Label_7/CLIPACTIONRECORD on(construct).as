on(construct){
   while(true)
   {
      if(!(0x2F95F60F & 0x2F95F60F))
      {
         if(false)
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
         enabled = true;
         html = false;
         multiline = false;
         styleName = "BrownLeftSmallLabel";
         §§push("text");
         §§push("");
         if(!ord("\b"))
         {
            §§goto(addr1ee05);
         }
      }
      set(§§pop(),§§pop());
      §§push("wordWrap");
      §§push(false);
      break;
   }
   set(§§pop(),§§pop());
   addr1ee05:
   §§pop()();
}
