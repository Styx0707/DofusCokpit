on(construct){
   while(true)
   {
      if(false)
      {
         if(!ord("\x02"))
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
         styleName = "WhiteLeftMediumLabel";
         §§push("text");
         §§push("");
         if(!getTimer())
         {
            §§goto(addr18af6);
         }
      }
      set(§§pop(),§§pop());
      wordWrap = false;
      break;
   }
   addr18af6:
   getProperty(§§pop(), _X);
}
