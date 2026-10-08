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
         §§push("\x07");
      }
      if(!ord(§§pop()))
      {
         break;
      }
      enabled = true;
      html = false;
      multiline = false;
      styleName = "BrownLeftSmallBoldLabel";
      text = "";
      §§push("wordWrap");
      §§push(false);
      if(!ord("\x02"))
      {
         §§push(getProperty(§§pop(), _X));
      }
      else
      {
         addr18e05:
         set(§§pop(),§§pop());
      }
      return;
   }
   §§goto(addr18e05);
}
