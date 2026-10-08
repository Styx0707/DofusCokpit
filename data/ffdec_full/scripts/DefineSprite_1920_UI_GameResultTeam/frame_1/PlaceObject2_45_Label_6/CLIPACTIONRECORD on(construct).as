on(construct){
   while(true)
   {
      if(!ord("\x03"))
      {
         if(false)
         {
            break;
         }
      }
      else
      {
         §§push("\x02");
      }
      if(ord(§§pop()))
      {
         enabled = true;
         html = false;
         multiline = false;
         styleName = "WhiteCenterSmallLabel";
         §§push("text");
         §§push("");
         if(!getTimer())
         {
            §§goto(addr12923);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   wordWrap = false;
   addr12923:
   getProperty(§§pop(), _X);
}
