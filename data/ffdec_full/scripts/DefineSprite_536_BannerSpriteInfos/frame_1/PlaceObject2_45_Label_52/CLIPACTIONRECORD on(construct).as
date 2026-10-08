on(construct){
   while(true)
   {
      if(false)
      {
         if(!ord("\n"))
         {
            break;
         }
      }
      else
      {
         §§push("\x03");
      }
      if(ord(§§pop()))
      {
         enabled = true;
         html = false;
         multiline = false;
         styleName = "BlueLeftExtraSmallLabel";
         §§push("text");
         §§push("");
         if(!(getTimer() + 1))
         {
            startDrag(§§pop(),§§pop(),§§pop(),§§pop(),§§pop(),§§pop());
            §§goto(addr35e0f);
         }
      }
      set(§§pop(),§§pop());
      §§push("wordWrap");
      §§push(false);
      break;
   }
   set(§§pop(),§§pop());
   addr35e0f:
}
