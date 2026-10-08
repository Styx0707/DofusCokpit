on(construct){
   while(true)
   {
      if(false)
      {
         if(!(true or true))
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
         enabled = true;
         html = false;
         multiline = false;
         styleName = "BrownLeftSmallLabel";
         §§push("text");
         §§push("");
         if(!ord("\x07"))
         {
            §§goto(addr1800a);
         }
      }
      set(§§pop(),§§pop());
      break;
   }
   wordWrap = false;
   addr1800a:
   getProperty(§§pop(), _X);
}
